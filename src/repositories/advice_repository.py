"""Advice repository."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.knowledge import Advice
from .knowledge_repository_base import KnowledgeRepositoryBase


class AdviceRepository(KnowledgeRepositoryBase[Advice]):
    def __init__(self) -> None:
        super().__init__(Advice, "advice_id")

    async def get_by_cause_id(
        self, cause_id: UUID, session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[Advice]:
        result = await session.execute(
            select(Advice)
            .where(Advice.cause_id == cause_id)
            .order_by(Advice.advice_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
