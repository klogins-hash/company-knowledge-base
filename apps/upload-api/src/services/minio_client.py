"""MinIO client service"""
import logging
from minio import Minio
from minio.error import S3Error
from src.config import settings

logger = logging.getLogger(__name__)

# Global MinIO client
minio_client: Minio = None


async def init_minio():
    """Initialize MinIO client and create bucket if needed"""
    global minio_client

    try:
        # Create MinIO client
        minio_client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure
        )

        logger.info(f"MinIO client initialized for endpoint: {settings.minio_endpoint}")

        # Create bucket if it doesn't exist
        bucket_name = settings.minio_bucket
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)
            logger.info(f"Created bucket: {bucket_name}")
        else:
            logger.info(f"Bucket already exists: {bucket_name}")

    except S3Error as e:
        logger.error(f"MinIO error: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to initialize MinIO: {e}")
        raise


def get_client() -> Minio:
    """Get the MinIO client"""
    if not minio_client:
        raise RuntimeError("MinIO client not initialized")
    return minio_client
