"""Situation service."""

from sqlalchemy.ext.asyncio import AsyncSession

from ..models.knowledge import Situation
from ..repositories.situation_repository import SituationRepository
from ..schemas.situation import SituationCreate, SituationRead, SituationUpdate
from .base import BaseService


class SituationService(
    BaseService[Situation, SituationCreate, SituationUpdate, SituationRead]
):
    def __init__(self, repository: SituationRepository):
        super().__init__(
            repository=repository,
            entity_name="Situation",
            create_schema=SituationCreate,
            update_schema=SituationUpdate,
            read_schema=SituationRead,
        )
        self.situation_repo = repository

    async def find_by_controlled_value(
        self,
        controlled_param: str,
        value: float,
        session: AsyncSession,
    ) -> SituationRead | None:
        situation = await self.situation_repo.find_by_controlled_value(
            controlled_param, value, session
        )
        if situation is None:
            return None
        return SituationRead.model_validate(situation)
