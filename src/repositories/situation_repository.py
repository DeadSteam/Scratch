"""Situation repository."""

from ..models.knowledge import Situation
from .knowledge_repository_base import KnowledgeRepositoryBase


class SituationRepository(KnowledgeRepositoryBase[Situation]):
    def __init__(self) -> None:
        super().__init__(Situation, "situation_id")
