"""Cause service."""

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.cause_repository import CauseRepository
from ..repositories.situation_repository import SituationRepository
from ..schemas.cause import CauseCreate, CauseRead, CauseUpdate
from .exceptions import NotFoundError
from .knowledge_service_base import KnowledgeServiceBase


class CauseService(KnowledgeServiceBase[object, CauseCreate, CauseUpdate, CauseRead]):
    def __init__(
        self,
        repository: CauseRepository,
        situation_repository: SituationRepository,
    ):
        super().__init__(
            repository=repository,
            entity_name="Cause",
            create_schema=CauseCreate,
            update_schema=CauseUpdate,
            read_schema=CauseRead,
        )
        self.situation_repo = situation_repository

    async def _check_constraints(
        self,
        data: dict[str, Any],
        session: AsyncSession,
        exclude_id: UUID | None = None,
    ) -> None:
        situation_id = data.get("situation_id")
        if situation_id is not None and not await self.situation_repo.exists(situation_id, session):
            raise NotFoundError("Situation", situation_id)

    async def get_by_situation_id(
        self,
        situation_id: UUID,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> list[CauseRead]:
        if not await self.situation_repo.exists(situation_id, session):
            raise NotFoundError("Situation", situation_id)
        causes = await self.repository.get_by_situation_id(situation_id, session, skip, limit)
        return [self.read_schema.model_validate(c) for c in causes]
