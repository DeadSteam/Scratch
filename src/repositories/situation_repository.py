"""Situation repository."""

from ..models.knowledge import Situation
from .base import CachedRepositoryImpl


class SituationRepository(CachedRepositoryImpl[Situation]):
    def __init__(self) -> None:
        super().__init__(Situation)
