"""Advice repository."""

from collections.abc import Iterable
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.knowledge import Advice
from .base import CachedRepositoryImpl


class AdviceRepository(CachedRepositoryImpl[Advice]):
    def __init__(self) -> None:
        super().__init__(Advice)

    async def get_by_cause_id(
        self, cause_id: UUID, session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[Advice]:
        result = await session.execute(
            select(Advice)
            .where(Advice.cause_id == cause_id)
            .order_by(Advice.id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_cause_ids(
        self, cause_ids: Iterable[UUID], session: AsyncSession
    ) -> dict[UUID, list[Advice]]:
        """Batch-load advices for many causes in ONE query.

        Returns a dict keyed by cause_id. Used by knowledge_summary to avoid
        the N+1 pattern (one query per cause).
        """
        ids = list(cause_ids)
        if not ids:
            return {}
        result = await session.execute(
            select(Advice).where(Advice.cause_id.in_(ids)).order_by(Advice.id)
        )
        bucket: dict[UUID, list[Advice]] = {cid: [] for cid in ids}
        for advice in result.scalars().all():
            cid = advice.cause_id
            if cid is None:
                continue
            target = bucket.get(cid)
            if target is None:
                target = []
                bucket[cid] = target
            target.append(advice)
        return bucket
