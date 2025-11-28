"""Database service using asyncpg"""
import asyncpg
import logging
from typing import Optional
from src.config import settings

logger = logging.getLogger(__name__)

# Global connection pool
_pool: Optional[asyncpg.Pool] = None


async def init_db():
    """Initialize database connection pool"""
    global _pool

    try:
        _pool = await asyncpg.create_pool(
            settings.database_url,
            min_size=2,
            max_size=10,
            command_timeout=60
        )
        logger.info("Database pool created successfully")

        # Test connection
        async with _pool.acquire() as conn:
            await conn.fetchval('SELECT 1')
            logger.info("Database connection test successful")

    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def close_db():
    """Close database connection pool"""
    global _pool

    if _pool:
        await _pool.close()
        logger.info("Database pool closed")


async def get_conn():
    """Get a database connection from the pool"""
    if not _pool:
        raise RuntimeError("Database pool not initialized")
    return _pool.acquire()


async def execute_query(query: str, *args):
    """Execute a query and return results"""
    async with get_conn() as conn:
        return await conn.fetch(query, *args)


async def execute_one(query: str, *args):
    """Execute a query and return one result"""
    async with get_conn() as conn:
        return await conn.fetchrow(query, *args)


async def execute_command(query: str, *args):
    """Execute a command (INSERT, UPDATE, DELETE)"""
    async with get_conn() as conn:
        return await conn.execute(query, *args)
