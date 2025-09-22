"""
Database configuration and session management.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from .settings import get_settings

settings = get_settings()

# Create async engine with proper SSL configuration for Neon
connect_args = {}
database_url = settings.database.url

# Ensure we're using asyncpg driver for async operations
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
elif not database_url.startswith("postgresql+asyncpg://"):
    # If it's already postgresql+asyncpg://, keep it as is
    pass

# Handle Neon SSL configuration
if "postgresql" in database_url and "neon" in database_url:
    # Remove any sslmode parameters from URL and handle via connect_args
    if "sslmode=" in database_url:
        database_url = database_url.split("?")[0]  # Remove query parameters
    
    connect_args = {
        "ssl": "require"
    }
elif "postgresql" in database_url:
    connect_args = {
        "server_settings": {
            "jit": "off"
        }
    }

# Use NullPool for Neon in production (serverless-friendly)
if settings.app.environment == "production" and "neon" in database_url:
    async_engine = create_async_engine(
        database_url,
        echo=settings.database.echo,
        poolclass=NullPool,
        pool_pre_ping=True,
        connect_args=connect_args,
    )
else:
    # Use regular pooling for development
    async_engine = create_async_engine(
        database_url,
        echo=settings.database.echo,
        pool_size=settings.database.pool_size,
        max_overflow=settings.database.max_overflow,
        pool_pre_ping=True,
        connect_args=connect_args,
    )

# Create sync engine for Alembic
sync_database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
sync_connect_args = {}

# Ensure sync URL uses psycopg2 (default PostgreSQL driver for sync operations)
if sync_database_url.startswith("postgresql+asyncpg://"):
    sync_database_url = sync_database_url.replace("postgresql+asyncpg://", "postgresql://", 1)

if "postgresql" in sync_database_url and "neon" in sync_database_url:
    sync_connect_args = {
        "sslmode": "require"
    }
elif "postgresql" in sync_database_url:
    sync_connect_args = {
        "options": "-c jit=off"
    }

# Use NullPool for sync engine in production too
if settings.app.environment == "production" and "neon" in sync_database_url:
    sync_engine = create_engine(
        sync_database_url,
        echo=settings.database.echo,
        poolclass=NullPool,
        pool_pre_ping=True,
        connect_args=sync_connect_args,
    )
else:
    sync_engine = create_engine(
        sync_database_url,
        echo=settings.database.echo,
        pool_size=settings.database.pool_size,
        max_overflow=settings.database.max_overflow,
        pool_pre_ping=True,
        connect_args=sync_connect_args,
    )

# Session makers
AsyncSessionLocal = async_sessionmaker(
    async_engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=sync_engine
)

# Base model with naming convention for constraints
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)
Base = declarative_base(metadata=metadata)


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database session."""
    async with get_db_session() as session:
        yield session


def get_sync_db():
    """Get synchronous database session for Alembic."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
