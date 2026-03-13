from sqlmodel import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.pool import AsyncAdaptedQueuePool
import os
from typing import AsyncGenerator
from contextlib import asynccontextmanager


# Get database URL from environment, with a fallback to SQLite for development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./todo_chatbot_dev.db")

# Neon (and most providers) give plain postgresql:// — convert for asyncpg async driver
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# For sync operations like Alembic migrations
if DATABASE_URL.startswith("postgresql+asyncpg://"):
    SYNC_DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
elif DATABASE_URL.startswith("sqlite+aiosqlite://"):
    SYNC_DATABASE_URL = DATABASE_URL.replace("sqlite+aiosqlite://", "sqlite://")
else:
    SYNC_DATABASE_URL = DATABASE_URL

# Create async engine with connection pooling configuration for application use
if DATABASE_URL.startswith("postgresql"):
    async_engine: AsyncEngine = create_async_engine(
        DATABASE_URL,
        poolclass=AsyncAdaptedQueuePool,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=300,    # Recycle connections every 5 minutes
        echo=False           # Set to True for SQL query logging in development
    )
else:
    # For SQLite, use the aiosqlite async driver
    from sqlalchemy.ext.asyncio import create_async_engine
    async_engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        connect_args={
            "check_same_thread": False,  # Required for SQLite
            "detect_types": 3  # Enables both PARSE_DECLTYPES and PARSE_COLNAMES
        }  # Character encoding is handled by aiosqlite automatically
    )

# Create sync engine for Alembic migrations and sync operations
if SYNC_DATABASE_URL.startswith("postgresql"):
    sync_engine = create_engine(
        SYNC_DATABASE_URL,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=300,    # Recycle connections every 5 minutes
        echo=False           # Set to True for SQL query logging in development
    )
else:
    # For SQLite sync operations
    sync_engine = create_engine(
        SYNC_DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False}  # Required for SQLite
    )


from sqlmodel.ext.asyncio.session import AsyncSession


async def get_async_session() -> AsyncGenerator:
    """
    Get async database session for dependency injection
    """
    async with AsyncSession(async_engine) as session:
        yield session