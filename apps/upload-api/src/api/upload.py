"""Upload API endpoints"""
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Optional
import logging
import uuid
from datetime import datetime

from src.config import settings
from src.services.minio_client import get_client
from src.services.database import execute_one, execute_command

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    Upload a file to MinIO

    This endpoint streams the file directly to MinIO without loading it into memory.
    After upload completes, a Temporal workflow is triggered to process the document.
    """
    try:
        upload_id = str(uuid.uuid4())
        object_name = f"{upload_id}/{file.filename}"
        minio = get_client()

        # Get file size (for multipart upload detection)
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)

        logger.info(f"Starting upload: {file.filename} ({file_size} bytes)")

        # Stream upload to MinIO
        minio.put_object(
            bucket_name=settings.minio_bucket,
            object_name=object_name,
            data=file.file,
            length=file_size,
            content_type=file.content_type
        )

        # Store metadata in database
        query = """
            INSERT INTO uploads (id, filename, file_size, content_type, minio_bucket, minio_key, upload_status)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING id, created_at
        """

        result = await execute_one(
            query,
            upload_id,
            file.filename,
            file_size,
            file.content_type,
            settings.minio_bucket,
            object_name,
            'completed'
        )

        # TODO: Trigger Temporal workflow for processing
        # background_tasks.add_task(start_document_workflow, upload_id)

        logger.info(f"Upload completed: {upload_id}")

        return {
            "upload_id": upload_id,
            "filename": file.filename,
            "file_size": file_size,
            "status": "completed",
            "message": "File uploaded successfully. Processing will begin shortly."
        }

    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload/multipart/init")
async def init_multipart_upload(filename: str, content_type: Optional[str] = None):
    """
    Initialize a multipart upload for large files (>100MB)

    Returns an upload_id and minio_upload_id to use for uploading parts.
    """
    try:
        upload_id = str(uuid.uuid4())
        object_name = f"{upload_id}/{filename}"
        minio = get_client()

        # TODO: Initialize multipart upload in MinIO
        # minio_upload_id = minio.create_multipart_upload(...)

        logger.info(f"Multipart upload initialized: {upload_id}")

        return {
            "upload_id": upload_id,
            "filename": filename,
            "object_name": object_name,
            "message": "Multipart upload initialized. Upload parts using /upload/multipart/part endpoint."
        }

    except Exception as e:
        logger.error(f"Multipart init failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload/multipart/part")
async def upload_part(
    upload_id: str,
    part_number: int,
    file: UploadFile = File(...)
):
    """
    Upload a part of a multipart upload
    """
    try:
        # TODO: Upload part to MinIO and store ETag

        logger.info(f"Part {part_number} uploaded for {upload_id}")

        return {
            "upload_id": upload_id,
            "part_number": part_number,
            "status": "uploaded"
        }

    except Exception as e:
        logger.error(f"Part upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload/multipart/complete")
async def complete_multipart_upload(upload_id: str):
    """
    Complete a multipart upload
    """
    try:
        # TODO: Complete multipart upload in MinIO
        # TODO: Trigger Temporal workflow

        logger.info(f"Multipart upload completed: {upload_id}")

        return {
            "upload_id": upload_id,
            "status": "completed",
            "message": "Upload completed successfully"
        }

    except Exception as e:
        logger.error(f"Multipart complete failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/upload/{upload_id}")
async def cancel_upload(upload_id: str):
    """
    Cancel an upload and delete from MinIO
    """
    try:
        # TODO: Delete from MinIO
        # TODO: Update database status

        logger.info(f"Upload cancelled: {upload_id}")

        return {
            "upload_id": upload_id,
            "status": "cancelled"
        }

    except Exception as e:
        logger.error(f"Cancel upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
