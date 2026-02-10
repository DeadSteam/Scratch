"""Database engines, session factories, and dependency providers.

Transaction management: session dependencies commit on success and
rollback on exception. Repositories must NOT call session.commit().
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from .config import settings
from .logging_config import get_logger

logger = get_logger(__name__)


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


# ---------------------------------------------------------------------------
# Database engines
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# Session factories
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# FastAPI dependencies (one transaction per request)
# ---------------------------------------------------------------------------
async def get_db_session() -> AsyncGenerator[AsyncSession]:
    """Dependency: main database session with auto commit/rollback."""
    async with MainSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_users_db_session() -> AsyncGenerator[AsyncSession]:
    """Dependency: users database session with auto commit/rollback."""
    async with UsersSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_knowledge_db_session() -> AsyncGenerator[AsyncSession]:
    """Dependency: knowledge base database session with auto commit/rollback."""
    if KnowledgeSessionLocal is None:
        logger.error(
            "knowledge_db_not_configured",
            reason="KNOWLEDGE_DATABASE_URL is not set",
        )
        raise RuntimeError(
            "Knowledge database is not configured (KNOWLEDGE_DATABASE_URL is not set)"
        )
    async with KnowledgeSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ---------------------------------------------------------------------------
# Explicit transaction context managers (for non-request code, e.g. startup)
# ---------------------------------------------------------------------------
@asynccontextmanager
async def get_db_transaction() -> AsyncGenerator[AsyncSession]:
    """Context manager for main database transactions."""
    async with MainSessionLocal() as session:
        try:
            logger.debug("db_transaction_started")
            yield session
            await session.commit()
            logger.debug("db_transaction_committed")
        except Exception:
            await session.rollback()
            logger.error("db_transaction_rolled_back")
            raise


@asynccontextmanager
async def get_users_db_transaction() -> AsyncGenerator[AsyncSession]:
    """Context manager for users database transactions."""
    async with UsersSessionLocal() as session:
        try:
            logger.debug("users_db_transaction_started")
            yield session
            await session.commit()
            logger.debug("users_db_transaction_committed")
        except Exception:
            await session.rollback()
            logger.error("users_db_transaction_rolled_back")
            raise


# ---------------------------------------------------------------------------
# Shutdown helper
# ---------------------------------------------------------------------------
async def close_db_connections() -> None:
    """Close all database connections."""
    logger.info("closing_db_connections")
    await main_engine.dispose()
    await users_engine.dispose()
    if knowledge_engine is not None:
        await knowledge_engine.dispose()
