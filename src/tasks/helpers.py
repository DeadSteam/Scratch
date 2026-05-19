"""Helpers for running async code inside synchronous Celery workers."""

from __future__ import annotations

import asyncio
from collections.abc import Coroutine
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import MainSessionLocal, UsersSessionLocal


def _reset_redis_singletons() -> None:
    """Drop module-level repo Redis clients so the next task rebinds them.

    Task-scoped event loops mean the previous loop is closed by the time
    a follow-up task runs; any `_redis_client` bound to that loop becomes
    invalid and raises "Event loop is closed". Resetting here avoids that
    for the repositories used by Celery tasks.
    """
    try:
        from . import experiment_tasks as _et
        from . import image_analysis_tasks as _iat

        for module in (_et, _iat):
            for attr in ("_image_repo", "_experiment_repo"):
                repo = getattr(module, attr, None)
                if repo is not None:
                    repo._redis_client = None
    except Exception:
        # Never let teardown break a task.
        pass


def run_async[T](coro: Coroutine[Any, Any, T]) -> T:
    """Execute an async coroutine in a fresh event loop.

    ``asyncio.run`` is preferred over manual loop/close: it cancels any
    straggling tasks and shuts down async generators (asyncpg/aioredis
    cleanup) so the next Celery invocation starts clean.
    """
    try:
        return asyncio.run(coro)
    finally:
        _reset_redis_singletons()


async def get_main_session() -> AsyncSession:
    """Create a standalone main DB session for use in tasks."""
    return MainSessionLocal()


async def get_users_session() -> AsyncSession:
    """Create a standalone users DB session for use in tasks."""
    return UsersSessionLocal()
