from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.user import User
from .base import CachedRepositoryImpl
from .interfaces import UserRepositoryInterface


class UserRepository(CachedRepositoryImpl[User], UserRepositoryInterface[User]):
    """User repository implementation."""

    def __init__(self) -> None:
        super().__init__(User)

    async def get_by_id_with_roles(
        self, user_id: UUID, session: AsyncSession
    ) -> User | None:
        """Get user by ID with roles eagerly loaded (bypasses cache).

        Used for authentication checks where roles must be present.
        """
        result = await session.execute(
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.roles))
        )
        return result.scalar_one_or_none()

    async def get_by_username(
        self, username: str, session: AsyncSession
    ) -> User | None:
        """Get user by username."""
        result = await session.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str, session: AsyncSession) -> User | None:
        """Get user by email."""
        result = await session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_active_users(
        self, session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[User]:
        """Get active users only."""
        result = await session.execute(
            select(User).where(User.is_active).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_username_cached(
        self, username: str, session: AsyncSession
    ) -> User | None:
        """Get user by username with cache check."""
        redis_client = await self._get_redis_client()
        cache_key = f"user:username:{username}"

        # Try cache first
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return User(**cached_data)

        # Get from database
        user = await self.get_by_username(username, session)
        if user:
            # Cache the user
            user_dict = {c.name: getattr(user, c.name) for c in user.__table__.columns}
            await redis_client.set(cache_key, user_dict)

        return user

    async def get_by_email_cached(
        self, email: str, session: AsyncSession
    ) -> User | None:
        """Get user by email with cache check."""
        redis_client = await self._get_redis_client()
        cache_key = f"user:email:{email}"

        # Try cache first
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return User(**cached_data)

        # Get from database
        user = await self.get_by_email(email, session)
        if user:
            # Cache the user
            user_dict = {c.name: getattr(user, c.name) for c in user.__table__.columns}
            await redis_client.set(cache_key, user_dict)

        return user

    async def count_active(self, session: AsyncSession) -> int:
        """Count active users."""
        result = await session.execute(select(func.count(User.id)).where(User.is_active))
        return result.scalar() or 0
