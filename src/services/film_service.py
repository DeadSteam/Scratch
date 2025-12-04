"""Film service."""
from typing import Dict, Any, List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseService
from .exceptions import AlreadyExistsError
from ..repositories.film_repository import FilmRepository
from ..schemas.film import FilmCreate, FilmUpdate, FilmRead
from ..models.film import Film


class FilmService(BaseService[Film, FilmCreate, FilmUpdate, FilmRead]):
    """Film service."""
    
    def __init__(self, repository: FilmRepository):
        super().__init__(
            repository=repository,
            entity_name="Film",
            create_schema=FilmCreate,
            update_schema=FilmUpdate,
            read_schema=FilmRead,
        )
        self.film_repo = repository
    
    async def _check_unique_constraints(
        self,
        data: Dict[str, Any],
        session: AsyncSession,
        exclude_id: Optional[UUID] = None
    ) -> None:
        """Check film name uniqueness."""
        if 'name' in data:
            existing = await self.film_repo.get_by_name(data['name'], session)
            if existing and (not exclude_id or existing.id != exclude_id):
                raise AlreadyExistsError("Film", "name", data['name'])
    
    async def search_by_name(
        self,
        name_pattern: str,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[FilmRead]:
        """Search films by name pattern."""
        films = await self.film_repo.search_by_name(name_pattern, session, skip, limit)
        return [self.read_schema.model_validate(f) for f in films]




















