import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from .config import settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


# Database engines
main_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
)

users_engine = create_async_engine(
    settings.USERS_DATABASE_URL,
    echo=settings.DB_ECHO,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
)

# Knowledge base engine (optional)
knowledge_engine = None
KnowledgeSessionLocal = None
if settings.KNOWLEDGE_DATABASE_URL:
    knowledge_engine = create_async_engine(
        settings.KNOWLEDGE_DATABASE_URL,
        echo=settings.DB_ECHO,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
    )
    KnowledgeSessionLocal = async_sessionmaker(
        bind=knowledge_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

# Session factories
MainSessionLocal = async_sessionmaker(
    bind=main_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

UsersSessionLocal = async_sessionmaker(
    bind=users_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get main database session."""
    async with MainSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_users_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get users database session."""
    logger.info(f"DEBUG: Creating users_db session with URL: {settings.USERS_DATABASE_URL}")
    async with UsersSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_knowledge_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get knowledge base database session."""
    if KnowledgeSessionLocal is None:
        raise RuntimeError(
            "Knowledge database is not configured (KNOWLEDGE_DATABASE_URL is not set)"
        )
    async with KnowledgeSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@asynccontextmanager
async def get_db_transaction() -> AsyncGenerator[AsyncSession, None]:
    """Context manager for database transactions."""
    async with MainSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_users_db_transaction() -> AsyncGenerator[AsyncSession, None]:
    """Context manager for users database transactions."""
    async with UsersSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def close_db_connections() -> None:
    """Close all database connections."""
    await main_engine.dispose()
    await users_engine.dispose()
    if knowledge_engine is not None:
        await knowledge_engine.dispose()
