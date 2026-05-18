"""Mixin for repositories keyed by a unique ``name`` field."""

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .base import CachedRepositoryImpl


class NamedEntityRepositoryMixin:
    """Shared get/search/count-by-name helpers for Film and EquipmentConfig."""

    model: type[Any]

    async def get_by_name(self, name: str, session: AsyncSession) -> Any | None:
        result = await session.execute(
            select(self.model).where(self.model.name == name)
        )
        return result.scalar_one_or_none()

    async def search_by_name(
        self, name_pattern: str, session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[Any]:
        result = await session.execute(
            select(self.model)
            .where(self.model.name.ilike(f"%{name_pattern}%"))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_search_by_name(
        self, name_pattern: str, session: AsyncSession
    ) -> int:
        result = await session.execute(
            select(func.count(self.model.id)).where(
                self.model.name.ilike(f"%{name_pattern}%")
            )
        )
        return result.scalar() or 0


class NamedEntityRepository(NamedEntityRepositoryMixin, CachedRepositoryImpl[Any]):
    """Base class for name-indexed cached entities."""
