"""Main FastAPI application"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from src.config import settings
from src.api import upload, status
from src.services.database import init_db, close_db
from src.services.minio_client import init_minio, minio_client


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Document Upload API...")

    # Initialize database
    await init_db()
    logger.info("Database initialized")

    # Initialize MinIO
    await init_minio()
    logger.info(f"MinIO initialized - bucket: {settings.minio_bucket}")

    yield

    # Shutdown
    logger.info("Shutting down Document Upload API...")
    await close_db()


# Create FastAPI app
app = FastAPI(
    title="Document Upload & Processing API",
    description="Upload large documents (10GB+) and process them with AI agents",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.environment,
        "minio_endpoint": settings.minio_endpoint,
        "temporal_host": settings.temporal_host
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Document Upload & Processing API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# Include routers
app.include_router(upload.router, prefix="/api/v1", tags=["upload"])
app.include_router(status.router, prefix="/api/v1", tags=["status"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.environment == "development"
    )
