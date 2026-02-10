"""User service with CRUD operations.

Authentication logic is in AuthService (SRP).
"""

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from ..core.security import get_password_hash
from ..models.user import User
from ..repositories.user_repository import UserRepository
from ..schemas.user import UserCreate, UserRead, UserUpdate
from .base import BaseService
from .exceptions import AlreadyExistsError, NotFoundError


class UserService(BaseService[User, UserCreate, UserUpdate, UserRead]):
    """User service with CRUD and uniqueness checks."""

    def __init__(self, repository: UserRepository):
        super().__init__(
            repository=repository,
            entity_name="User",
            create_schema=UserCreate,
            update_schema=UserUpdate,
            read_schema=UserRead,
        )
        self.user_repo = repository

    async def _check_unique_constraints(
        self,
        data: dict[str, Any],
        session: AsyncSession,
        exclude_id: UUID | None = None,
    ) -> None:
        """Check username and email uniqueness."""
        if "username" in data:
            existing = await self.user_repo.get_by_username(data["username"], session)
            if existing and (not exclude_id or existing.id != exclude_id):
                raise AlreadyExistsError("User", "username", data["username"])
        if "email" in data:
            existing = await self.user_repo.get_by_email(data["email"], session)
            if existing and (not exclude_id or existing.id != exclude_id):
                raise AlreadyExistsError("User", "email", data["email"])

    async def create(self, data: UserCreate, session: AsyncSession) -> UserRead:
        """Create user with hashed password."""
        user_data_dict = data.model_dump()
        await self._check_unique_constraints(user_data_dict, session)

        user_data = data.model_dump(exclude={"password"})
        user_data["password_hash"] = get_password_hash(data.password)

        user = await self.user_repo.create(user_data, session)
        return self.read_schema.model_validate(user)

    async def update(
        self, entity_id: UUID, data: UserUpdate, session: AsyncSession
    ) -> UserRead:
        """Update user, hash password if provided."""
        user_data = data.model_dump(exclude_unset=True, exclude={"password"})
        if data.password:
            user_data["password_hash"] = get_password_hash(data.password)

        if not user_data:
            return await self.get_by_id(entity_id, session)

        await self._check_unique_constraints(user_data, session, entity_id)
        user = await self.user_repo.update(entity_id, user_data, session)
        return self.read_schema.model_validate(user)

    async def get_for_auth(self, user_id: UUID, session: AsyncSession) -> UserRead:
        """Get user for authentication verification (with roles, no cache).

        This bypasses the Redis cache to ensure roles are always present.
        Used exclusively by ``get_current_user`` dependency.
        """
        user = await self.user_repo.get_by_id_with_roles(user_id, session)
        if not user:
            raise NotFoundError("User", user_id)
        return self.read_schema.model_validate(user)

    async def get_by_username(self, username: str, session: AsyncSession) -> UserRead:
        """Get user by username (cached)."""
        user = await self.user_repo.get_by_username_cached(username, session)
        if not user:
            raise NotFoundError("User", username)
        return self.read_schema.model_validate(user)

    async def get_by_email(self, email: str, session: AsyncSession) -> UserRead:
        """Get user by email (cached)."""
        user = await self.user_repo.get_by_email_cached(email, session)
        if not user:
            raise NotFoundError("User", email)
        return self.read_schema.model_validate(user)

    async def get_active_users(
        self, session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[UserRead]:
        """Get active users only."""
        users = await self.user_repo.get_active_users(session, skip, limit)
        return [self.read_schema.model_validate(u) for u in users]

    async def deactivate_user(self, user_id: UUID, session: AsyncSession) -> UserRead:
        """Deactivate user account."""
        user = await self.user_repo.update(user_id, {"is_active": False}, session)
        if not user:
            raise NotFoundError("User", user_id)
        return self.read_schema.model_validate(user)

    async def activate_user(self, user_id: UUID, session: AsyncSession) -> UserRead:
        """Activate user account."""
        user = await self.user_repo.update(user_id, {"is_active": True}, session)
        if not user:
            raise NotFoundError("User", user_id)
        return self.read_schema.model_validate(user)

    async def count(self, session: AsyncSession) -> int:
        """Count total users."""
        return await self.user_repo.count(session)

    async def count_active(self, session: AsyncSession) -> int:
        """Count active users."""
        return await self.user_repo.count_active(session)
