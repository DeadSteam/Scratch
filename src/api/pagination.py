"""Shared pagination helpers for API responses."""

from .responses import PaginatedResponse


def build_paginated_response[T](
    items: list[T],
    total: int,
    skip: int,
    limit: int,
) -> PaginatedResponse[T]:
    """Build a consistent paginated API response."""
    return PaginatedResponse(
        success=True,
        data=items,
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + len(items)) < total,
    )
