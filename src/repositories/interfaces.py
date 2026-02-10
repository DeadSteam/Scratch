from abc import ABC, abstractmethod
from typing import Any, TypeVar
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class BaseRepository[T](ABC):
    """Base repository interface following Repository pattern."""

    @abstractmethod
    async def get_by_id(self, id: UUID, session: AsyncSession) -> T | None:
        """Get entity by ID."""
        pass

    @abstractmethod
    async def get_all(
        self, session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[T]:
        """Get all entities with pagination."""
        pass

    @abstractmethod
    async def create(self, data: dict[str, Any], session: AsyncSession) -> T:
        """Create new entity."""
        pass

    @abstractmethod
    async def update(
        self, id: UUID, data: dict[str, Any], session: AsyncSession
    ) -> T | None:
        """Update entity by ID."""
        pass

    @abstractmethod
    async def delete(self, id: UUID, session: AsyncSession) -> bool:
        """Delete entity by ID."""
        pass

    @abstractmethod
    async def exists(self, id: UUID, session: AsyncSession) -> bool:
        """Check if entity exists by ID."""
        pass

    @abstractmethod
    async def count(self, session: AsyncSession) -> int:
        """Get total count of entities."""
        pass


class CachedRepository(BaseRepository[T], ABC):
    """Repository with caching capabilities."""

    @abstractmethod
    async def get_by_id_cached(self, id: UUID, session: AsyncSession) -> T | None:
        """Get entity by ID with cache check."""
        pass

    @abstractmethod
    async def get_all_cached(
        self, session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[T]:
        """Get all entities with cache check."""
        pass

    @abstractmethod
    async def invalidate_cache(self, id: UUID | None = None) -> None:
        """Invalidate cache for entity or all entities."""
        pass


class UserRepositoryInterface(BaseRepository[T], ABC):
    """User-specific repository interface."""

    @abstractmethod
    async def get_by_username(self, username: str, session: AsyncSession) -> T | None:
        """Get user by username."""
        pass

    @abstractmethod
    async def get_by_email(self, email: str, session: AsyncSession) -> T | None:
        """Get user by email."""
        pass

    @abstractmethod
    async def get_active_users(
        self, session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[T]:
        """Get active users only."""
        pass

    @abstractmethod
    async def count_active(self, session: AsyncSession) -> int:
        """Count active users."""
        pass


class ExperimentRepositoryInterface(BaseRepository[T], ABC):
    """Experiment-specific repository interface."""

    @abstractmethod
    async def get_by_user_id(
        self, user_id: UUID, session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[T]:
        """Get experiments by user ID."""
        pass

    @abstractmethod
    async def get_by_film_id(
        self, film_id: UUID, session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[T]:
        """Get experiments by film ID."""
        pass

    @abstractmethod
    async def get_by_config_id(
        self, config_id: UUID, session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[T]:
        """Get experiments by config ID."""
        pass

    @abstractmethod
    async def get_with_images(self, id: UUID, session: AsyncSession) -> T | None:
        """Get experiment with related images."""
        pass

    @abstractmethod
    async def count_by_user_id(self, user_id: UUID, session: AsyncSession) -> int:
        """Count experiments by user ID."""
        pass

    @abstractmethod
    async def count_by_film_id(self, film_id: UUID, session: AsyncSession) -> int:
        """Count experiments by film ID."""
        pass

    @abstractmethod
    async def count_by_config_id(self, config_id: UUID, session: AsyncSession) -> int:
        """Count experiments by config ID."""
        pass
