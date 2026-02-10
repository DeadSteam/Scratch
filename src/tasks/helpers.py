"""Helpers for running async code inside synchronous Celery workers."""

from __future__ import annotations

import asyncio
from collections.abc import Coroutine
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import MainSessionLocal, UsersSessionLocal


def run_async[T](coro: Coroutine[Any, Any, T]) -> T:
    """Execute an async coroutine in a new event loop.

    Celery workers are synchronous by default; this helper creates
    a fresh loop for each task invocation.
    """
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def get_main_session() -> AsyncSession:
    """Create a standalone main DB session for use in tasks."""
    return MainSessionLocal()


async def get_users_session() -> AsyncSession:
    """Create a standalone users DB session for use in tasks."""
    return UsersSessionLocal()
