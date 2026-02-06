from typing import Any, TypeVar, cast
from uuid import UUID

from sqlalchemy import delete, insert, select, update
from sqlalchemy.engine import CursorResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from ..core.logging_config import get_logger
from ..core.redis import RedisClient, get_redis_client
from .interfaces import BaseRepository

T = TypeVar("T", bound=DeclarativeBase)


class BaseRepositoryImpl[T](BaseRepository[T]):
    """Base repository implementation with common CRUD operations."""

    def __init__(self, model: type[T]) -> None:
        self.model = model
        self._redis_client: RedisClient | None = None
        self._logger = get_logger(f"repo.{self.model.__tablename__}")

    async def _get_redis_client(self) -> RedisClient:
        """Lazy initialization of Redis client."""
        if self._redis_client is None:
            self._logger.debug("redis_client_init")
            self._redis_client = await get_redis_client()
        return self._redis_client

    def _generate_cache_key(
        self, id: UUID | None = None, query_type: str = "all", **kwargs: Any
    ) -> str:
        """Generate cache key for entity."""
        if id:
            return f"{self.model.__tablename__}:id:{id}"
        elif query_type == "all":
            return f"{self.model.__tablename__}:all"
        else:
            # For custom queries, create key from parameters
            params = "_".join(f"{k}:{v}" for k, v in sorted(kwargs.items()))
            return f"{self.model.__tablename__}:{query_type}:{params}"

    async def get_by_id(self, id: UUID, session: AsyncSession) -> T | None:
        """Get entity by ID."""
        self._logger.debug("get_by_id", id=str(id))
        pk = self.model.id
        result = await session.execute(select(self.model).where(pk == id))
        entity = result.scalar_one_or_none()
        self._logger.debug("get_by_id_result", id=str(id), found=entity is not None)
        return entity

    async def get_all(
        self, session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[T]:
        """Get all entities with pagination."""
        self._logger.debug("get_all", skip=skip, limit=limit)
        result = await session.execute(select(self.model).offset(skip).limit(limit))
        entities = list(result.scalars().all())
        self._logger.debug("get_all_result", count=len(entities))
        return entities

    async def create(self, data: dict[str, Any], session: AsyncSession) -> T:
        """Create new entity."""
        self._logger.info("create", data_keys=list(data.keys()))
        stmt = insert(self.model).values(**data).returning(self.model)
        result = await session.execute(stmt)
        await session.commit()
        entity = result.scalar_one()
        self._logger.info("create_result")
        return entity

    async def update(
        self, id: UUID, data: dict[str, Any], session: AsyncSession
    ) -> T | None:
        """Update entity by ID."""
        self._logger.info("update", id=str(id), data_keys=list(data.keys()))
        pk = self.model.id
        stmt = update(self.model).where(pk == id).values(**data).returning(self.model)
        result = await session.execute(stmt)
        await session.commit()
        entity = result.scalar_one_or_none()
        self._logger.info("update_result", id=str(id), found=entity is not None)
        return entity

    async def delete(self, id: UUID, session: AsyncSession) -> bool:
        """Delete entity by ID."""
        self._logger.info("delete", id=str(id))
        pk = self.model.id
        stmt = delete(self.model).where(pk == id)
        result = await session.execute(stmt)
        await session.commit()
        deleted = cast(CursorResult[Any], result).rowcount > 0
        self._logger.info("delete_result", id=str(id), deleted=deleted)
        return deleted

    async def exists(self, id: UUID, session: AsyncSession) -> bool:
        """Check if entity exists by ID."""
        self._logger.debug("exists", id=str(id))
        pk = self.model.id
        result = await session.execute(select(pk).where(pk == id))
        exists = result.scalar_one_or_none() is not None
        self._logger.debug("exists_result", id=str(id), exists=exists)
        return exists

    async def count(self, session: AsyncSession) -> int:
        """Get total count of entities."""
        self._logger.debug("count_started")
        pk = self.model.id
        result = await session.execute(select(pk))
        count = len(result.scalars().all())
        self._logger.debug("count_result", count=count)
        return count


class CachedRepositoryImpl[T](BaseRepositoryImpl[T]):
    """Repository implementation with Redis caching."""

    async def get_by_id_cached(self, id: UUID, session: AsyncSession) -> T | None:
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
            # Cache the entity (DeclarativeBase instances have __table__)
            table = getattr(entity, "__table__", None)
            entity_dict = (
                {c.name: getattr(entity, c.name) for c in table.columns}
                if table is not None
                else {}
            )
            await redis_client.set(cache_key, entity_dict)

        return entity

    async def get_all_cached(
        self, session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[T]:
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
            # Cache the entities (DeclarativeBase instances have __table__)
            entities_dict = []
            for entity in entities:
                table = getattr(entity, "__table__", None)
                entities_dict.append(
                    {c.name: getattr(entity, c.name) for c in table.columns}
                    if table is not None
                    else {}
                )
            await redis_client.set(cache_key, entities_dict)

        return entities

    async def invalidate_cache(self, id: UUID | None = None) -> None:
        """Invalidate cache for entity or all entities."""
        redis_client = await self._get_redis_client()

        if id:
            # Invalidate specific entity cache
            cache_key = self._generate_cache_key(id=id)
            await redis_client.delete(cache_key)

        # Always invalidate "all" cache
        all_cache_key = self._generate_cache_key(query_type="all")
        await redis_client.delete(all_cache_key)

    async def create(self, data: dict[str, Any], session: AsyncSession) -> T:
        """Create entity and invalidate cache."""
        entity = await super().create(data, session)
        await self.invalidate_cache()
        return entity

    async def update(
        self, id: UUID, data: dict[str, Any], session: AsyncSession
    ) -> T | None:
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
