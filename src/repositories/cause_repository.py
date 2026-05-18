"""Cause repository."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.knowledge import Cause
from .base import CachedRepositoryImpl


class CauseRepository(CachedRepositoryImpl[Cause]):
    def __init__(self) -> None:
        super().__init__(Cause)

    async def get_by_situation_id(
        self, situation_id: UUID, session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[Cause]:
        result = await session.execute(
            select(Cause)
            .where(Cause.situation_id == situation_id)
            .order_by(Cause.id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_by_situation_id(
        self, situation_id: UUID, session: AsyncSession
    ) -> int:
        result = await session.execute(
            select(func.count(Cause.id)).where(Cause.situation_id == situation_id)
        )
        return result.scalar() or 0
