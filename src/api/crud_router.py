"""Helpers for repetitive CRUD list endpoints."""

from collections.abc import Awaitable, Callable
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from .pagination import build_paginated_response
from .responses import PaginatedResponse


async def paginated_list[T](
    session: AsyncSession,
    skip: int,
    limit: int,
    *,
    list_fn: Callable[..., Awaitable[list[T]]],
    count_fn: Callable[..., Awaitable[int]],
    **list_kwargs: object,
) -> PaginatedResponse[T]:
    """Fetch a page of items and build a paginated response."""
    items = await list_fn(session, skip, limit, **list_kwargs)
    total = await count_fn(session, **list_kwargs)
    return build_paginated_response(items, total, skip, limit)


async def paginated_list_by_parent[T](
    parent_id: UUID,
    session: AsyncSession,
    skip: int,
    limit: int,
    *,
    list_fn: Callable[..., Awaitable[list[T]]],
    count_fn: Callable[..., Awaitable[int]],
) -> PaginatedResponse[T]:
    """Fetch a page of child items scoped to a parent ID."""
    items = await list_fn(parent_id, session, skip, limit)
    total = await count_fn(parent_id, session)
    return build_paginated_response(items, total, skip, limit)
