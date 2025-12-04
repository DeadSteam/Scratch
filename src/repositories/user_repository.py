from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .base import CachedRepositoryImpl
from .interfaces import UserRepositoryInterface
from ..models.user import User


class UserRepository(CachedRepositoryImpl[User], UserRepositoryInterface[User]):
    """User repository implementation."""
    
    def __init__(self):
        super().__init__(User)
    
    async def get_by_username(self, username: str, session: AsyncSession) -> Optional[User]:
        """Get user by username."""
        result = await session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str, session: AsyncSession) -> Optional[User]:
        """Get user by email."""
        result = await session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_active_users(self, session: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
        """Get active users only."""
        result = await session.execute(
            select(User)
            .where(User.is_active == True)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_by_username_cached(self, username: str, session: AsyncSession) -> Optional[User]:
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
    
    async def get_by_email_cached(self, email: str, session: AsyncSession) -> Optional[User]:
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


