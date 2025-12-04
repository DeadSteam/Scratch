from typing import Any, Dict, Generic, List, Optional, Type, TypeVar
from uuid import UUID

from sqlalchemy import select, update, delete, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from .interfaces import BaseRepository
from ..core.redis import get_redis_client

T = TypeVar('T', bound=DeclarativeBase)


class BaseRepositoryImpl(BaseRepository[T], Generic[T]):
    """Base repository implementation with common CRUD operations."""
    
    def __init__(self, model: Type[T]):
        self.model = model
        self._redis_client = None
    
    async def _get_redis_client(self):
        """Lazy initialization of Redis client."""
        if self._redis_client is None:
            self._redis_client = await get_redis_client()
        return self._redis_client
    
    def _generate_cache_key(self, id: UUID = None, query_type: str = "all", **kwargs) -> str:
        """Generate cache key for entity."""
        if id:
            return f"{self.model.__tablename__}:id:{id}"
        elif query_type == "all":
            return f"{self.model.__tablename__}:all"
        else:
            # For custom queries, create key from parameters
            params = "_".join(f"{k}:{v}" for k, v in sorted(kwargs.items()))
            return f"{self.model.__tablename__}:{query_type}:{params}"
    
    async def get_by_id(self, id: UUID, session: AsyncSession) -> Optional[T]:
        """Get entity by ID."""
        result = await session.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()
    
    async def get_all(self, session: AsyncSession, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all entities with pagination."""
        result = await session.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return list(result.scalars().all())
    
    async def create(self, data: Dict[str, Any], session: AsyncSession) -> T:
        """Create new entity."""
        stmt = insert(self.model).values(**data).returning(self.model)
        result = await session.execute(stmt)
        await session.commit()
        return result.scalar_one()
    
    async def update(self, id: UUID, data: Dict[str, Any], session: AsyncSession) -> Optional[T]:
        """Update entity by ID."""
        stmt = update(self.model).where(self.model.id == id).values(**data).returning(self.model)
        result = await session.execute(stmt)
        await session.commit()
        return result.scalar_one_or_none()
    
    async def delete(self, id: UUID, session: AsyncSession) -> bool:
        """Delete entity by ID."""
        stmt = delete(self.model).where(self.model.id == id)
        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount > 0
    
    async def exists(self, id: UUID, session: AsyncSession) -> bool:
        """Check if entity exists by ID."""
        result = await session.execute(select(self.model.id).where(self.model.id == id))
        return result.scalar_one_or_none() is not None
    
    async def count(self, session: AsyncSession) -> int:
        """Get total count of entities."""
        result = await session.execute(select(self.model.id))
        return len(result.scalars().all())


class CachedRepositoryImpl(BaseRepositoryImpl[T], Generic[T]):
    """Repository implementation with Redis caching."""
    
    async def get_by_id_cached(self, id: UUID, session: AsyncSession) -> Optional[T]:
        """Get entity by ID with cache check."""
        redis_client = await self._get_redis_client()
        cache_key = self._generate_cache_key(id=id)
        
        # Try cache first
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            # Reconstruct entity from cached data
            return self.model(**cached_data)
        
        # Get from database
        entity = await self.get_by_id(id, session)
        if entity:
            # Cache the entity
            entity_dict = {c.name: getattr(entity, c.name) for c in entity.__table__.columns}
            await redis_client.set(cache_key, entity_dict)
        
        return entity
    
    async def get_all_cached(self, session: AsyncSession, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all entities with cache check."""
        redis_client = await self._get_redis_client()
        cache_key = self._generate_cache_key(query_type="all", skip=skip, limit=limit)
        
        # Try cache first
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return [self.model(**item) for item in cached_data]
        
        # Get from database
        entities = await self.get_all(session, skip, limit)
        if entities:
            # Cache the entities
            entities_dict = [
                {c.name: getattr(entity, c.name) for c in entity.__table__.columns}
                for entity in entities
            ]
            await redis_client.set(cache_key, entities_dict)
        
        return entities
    
    async def invalidate_cache(self, id: Optional[UUID] = None) -> None:
        """Invalidate cache for entity or all entities."""
        redis_client = await self._get_redis_client()
        
        if id:
            # Invalidate specific entity cache
            cache_key = self._generate_cache_key(id=id)
            await redis_client.delete(cache_key)
        
        # Always invalidate "all" cache
        all_cache_key = self._generate_cache_key(query_type="all")
        await redis_client.delete(all_cache_key)
    
    async def create(self, data: Dict[str, Any], session: AsyncSession) -> T:
        """Create entity and invalidate cache."""
        entity = await super().create(data, session)
        await self.invalidate_cache()
        return entity
    
    async def update(self, id: UUID, data: Dict[str, Any], session: AsyncSession) -> Optional[T]:
        """Update entity and invalidate cache."""
        entity = await super().update(id, data, session)
        if entity:
            await self.invalidate_cache(id)
        return entity
    
    async def delete(self, id: UUID, session: AsyncSession) -> bool:
        """Delete entity and invalidate cache."""
        success = await super().delete(id, session)
        if success:
            await self.invalidate_cache(id)
        return success


