"""Application configuration"""
from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path


def read_secret(secret_name: str) -> Optional[str]:
    """Read a Docker secret from /run/secrets/"""
    secret_path = Path(f"/run/secrets/{secret_name}")
    if secret_path.exists():
        return secret_path.read_text().strip()
    return None


class Settings(BaseSettings):
    """Application settings loaded from environment variables or Docker secrets"""

    # MinIO Configuration
    minio_endpoint: str = "supabase-minio:9000"
    minio_access_key: Optional[str] = None
    minio_secret_key: Optional[str] = None
    minio_bucket: str = "document-uploads"
    minio_secure: bool = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Override with Docker secrets if available
        self.minio_access_key = read_secret("minio_access_key") or self.minio_access_key
        self.minio_secret_key = read_secret("minio_secret_key") or self.minio_secret_key
        self.database_url = self._build_database_url()
        self.openai_api_key = read_secret("openai_api_key") or self.openai_api_key

    def _build_database_url(self) -> str:
        """Build database URL with password from secret if available"""
        password = read_secret("supabase_db_password")
        if password and hasattr(self, 'database_url'):
            # Replace password in existing URL
            import re
            return re.sub(r'(postgres:)[^@]*(@)', rf'\1{password}\2', self.database_url)
        return getattr(self, 'database_url', '')

    # Redis Configuration
    redis_host: str = "root_redis_1"
    redis_port: int = 6379
    redis_db: int = 0

    # PostgreSQL Configuration
    database_url: str

    # Temporal Configuration
    temporal_host: str = "temporal"
    temporal_port: int = 7233
    temporal_namespace: str = "default"
    temporal_task_queue: str = "document-processing"

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    max_upload_size: int = 10737418240  # 10GB
    chunk_size: int = 104857600  # 100MB
    workers: int = 4

    # Embedding API Configuration
    openai_api_key: Optional[str] = None
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536
    cohere_api_key: Optional[str] = None

    # Environment
    environment: str = "development"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
