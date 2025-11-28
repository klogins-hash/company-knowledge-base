"""Status API endpoints"""
from fastapi import APIRouter, HTTPException
import logging

from src.services.database import execute_one, execute_query

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/upload/{upload_id}/status")
async def get_upload_status(upload_id: str):
    """
    Get the status of an upload and its processing
    """
    try:
        query = """
            SELECT
                id,
                filename,
                file_size,
                content_type,
                upload_status,
                processing_status,
                created_at,
                completed_at,
                metadata
            FROM uploads
            WHERE id = $1
        """

        result = await execute_one(query, upload_id)

        if not result:
            raise HTTPException(status_code=404, detail="Upload not found")

        return {
            "upload_id": str(result['id']),
            "filename": result['filename'],
            "file_size": result['file_size'],
            "content_type": result['content_type'],
            "upload_status": result['upload_status'],
            "processing_status": result['processing_status'],
            "created_at": result['created_at'].isoformat() if result['created_at'] else None,
            "completed_at": result['completed_at'].isoformat() if result['completed_at'] else None,
            "metadata": result['metadata']
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get upload status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/uploads")
async def list_uploads(limit: int = 50, offset: int = 0):
    """
    List recent uploads
    """
    try:
        query = """
            SELECT
                id,
                filename,
                file_size,
                upload_status,
                processing_status,
                created_at
            FROM uploads
            ORDER BY created_at DESC
            LIMIT $1 OFFSET $2
        """

        results = await execute_query(query, limit, offset)

        uploads = []
        for row in results:
            uploads.append({
                "upload_id": str(row['id']),
                "filename": row['filename'],
                "file_size": row['file_size'],
                "upload_status": row['upload_status'],
                "processing_status": row['processing_status'],
                "created_at": row['created_at'].isoformat() if row['created_at'] else None
            })

        return {
            "uploads": uploads,
            "count": len(uploads),
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        logger.error(f"Failed to list uploads: {e}")
        raise HTTPException(status_code=500, detail=str(e))
