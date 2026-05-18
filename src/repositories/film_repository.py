from ..models.film import Film
from .base import CachedRepositoryImpl
from .named_entity import NamedEntityRepositoryMixin


class FilmRepository(NamedEntityRepositoryMixin, CachedRepositoryImpl[Film]):
    """Film repository implementation."""

    def __init__(self) -> None:
        super().__init__(Film)
