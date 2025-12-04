from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .base import CachedRepositoryImpl
from ..models.film import Film


class FilmRepository(CachedRepositoryImpl[Film]):
    """Film repository implementation."""
    
    def __init__(self):
        super().__init__(Film)
    
    async def get_by_name(self, name: str, session: AsyncSession) -> Optional[Film]:
        """Get film by name."""
        result = await session.execute(
            select(Film).where(Film.name == name)
        )
        return result.scalar_one_or_none()
    
    async def search_by_name(self, name_pattern: str, session: AsyncSession, skip: int = 0, limit: int = 100) -> List[Film]:
        """Search films by name pattern."""
        result = await session.execute(
            select(Film)
            .where(Film.name.ilike(f"%{name_pattern}%"))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())


