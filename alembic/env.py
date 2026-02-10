"""Shared Alembic environment for multi-database migrations.

Usage:
    alembic -x db=main      upgrade head
    alembic -x db=users     upgrade head
    alembic -x db=knowledge upgrade head

Without ``-x db=...`` the main (experiments) database is used by default.
"""

import asyncio
import os
import sys
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# ---------------------------------------------------------------------------
# Ensure project root is on sys.path so ``src.*`` imports work.
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))

# ---------------------------------------------------------------------------
# Import project models so autogenerate can detect tables.
# ---------------------------------------------------------------------------
# Force model registration (side-effect imports)
import src.models  # noqa: F401
from src.core.config import settings
from src.core.database import Base

# ---------------------------------------------------------------------------
# Determine target database from ``-x db=...`` CLI argument.
# ---------------------------------------------------------------------------
DB_CONFIG = {
    "main": settings.DATABASE_URL,
    "users": settings.USERS_DATABASE_URL,
    "knowledge": settings.KNOWLEDGE_DATABASE_URL or "",
}

_db_name_arg = context.get_x_argument(as_dictionary=True).get("db", "main")
if _db_name_arg not in DB_CONFIG:
    raise ValueError(
        f"Unknown database '{_db_name_arg}'. "
        f"Choose from: {', '.join(DB_CONFIG)}"
    )

target_url: str = DB_CONFIG[_db_name_arg]
if not target_url:
    raise RuntimeError(
        f"Database URL for '{_db_name_arg}' is not configured."
    )

# Alembic Config object (provides access to alembic.ini values).
config = context.config

# Override script_location to point to the correct versions dir.
config.set_main_option("script_location", f"alembic/{_db_name_arg}")

# Override sqlalchemy.url with the resolved database URL.
config.set_main_option("sqlalchemy.url", target_url.replace("%", "%%"))

# Standard Python logging from the .ini file.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata for autogenerate support.
target_metadata = Base.metadata

# ---------------------------------------------------------------------------
# Table filtering — only include tables belonging to the target database.
# ---------------------------------------------------------------------------
# Models bound to specific databases via __tablename__:
_USERS_TABLES = {"user", "role", "user_roles"}
_KNOWLEDGE_TABLES = {"situation", "cause", "advice"}


def include_name(name: str | None, type_: str, parent_names: dict) -> bool:  # type: ignore[type-arg]
    """Filter tables per database during autogenerate."""
    if type_ != "table" or name is None:
        return True
    if _db_name_arg == "users":
        return name in _USERS_TABLES
    if _db_name_arg == "knowledge":
        return name in _KNOWLEDGE_TABLES
    # main — everything *except* users/knowledge tables.
    return name not in (_USERS_TABLES | _KNOWLEDGE_TABLES)


# ---------------------------------------------------------------------------
# Migration runners
# ---------------------------------------------------------------------------
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (emit SQL without DB connection)."""
    context.configure(
        url=target_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_name=include_name,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:  # type: ignore[type-arg]
    """Configure context and run migrations inside a connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_name=include_name,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Create an async engine and run migrations."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (with a live DB connection)."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
