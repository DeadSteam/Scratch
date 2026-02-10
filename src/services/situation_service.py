"""Situation service."""

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
