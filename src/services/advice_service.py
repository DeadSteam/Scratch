"""Advice service."""

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.advice_repository import AdviceRepository
from ..repositories.cause_repository import CauseRepository
from ..schemas.advice import AdviceCreate, AdviceRead, AdviceUpdate
from .exceptions import NotFoundError
from .knowledge_service_base import KnowledgeServiceBase


class AdviceService(KnowledgeServiceBase[object, AdviceCreate, AdviceUpdate, AdviceRead]):
    def __init__(
        self,
        repository: AdviceRepository,
        cause_repository: CauseRepository,
    ):
        super().__init__(
            repository=repository,
            entity_name="Advice",
            create_schema=AdviceCreate,
            update_schema=AdviceUpdate,
            read_schema=AdviceRead,
        )
        self.cause_repo = cause_repository

    async def _check_constraints(
        self,
        data: dict[str, Any],
        session: AsyncSession,
        exclude_id: UUID | None = None,
    ) -> None:
        cause_id = data.get("cause_id")
        if cause_id is not None and not await self.cause_repo.exists(cause_id, session):
            raise NotFoundError("Cause", cause_id)

    async def get_by_cause_id(
        self,
        cause_id: UUID,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> list[AdviceRead]:
        if not await self.cause_repo.exists(cause_id, session):
            raise NotFoundError("Cause", cause_id)
        advices = await self.repository.get_by_cause_id(cause_id, session, skip, limit)
        return [self.read_schema.model_validate(a) for a in advices]
