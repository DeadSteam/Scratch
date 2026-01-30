"""User service with authentication logic."""

import logging
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from ..core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)
from ..models.user import User
from ..repositories.user_repository import UserRepository
from ..schemas.user import UserCreate, UserRead, UserUpdate
from .base import BaseService
from .exceptions import AlreadyExistsError, AuthenticationError, NotFoundError

logger = logging.getLogger(__name__)


class UserService(BaseService[User, UserCreate, UserUpdate, UserRead]):
    """User service with auth logic."""

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
        # Check uniqueness BEFORE hashing password
        user_data_dict = data.model_dump()
        await self._check_unique_constraints(user_data_dict, session)

        # Hash password and prepare data
        user_data = data.model_dump(exclude={"password"})
        user_data["password_hash"] = get_password_hash(data.password)

        # Create user
        user = await self.user_repo.create(user_data, session)
        return self.read_schema.model_validate(user)

    async def update(
        self, entity_id: UUID, data: UserUpdate, session: AsyncSession
    ) -> UserRead:
        """Update user, hash password if provided."""
        user_data = data.model_dump(exclude_unset=True, exclude={"password"})

        # Hash password if provided
        if data.password:
            user_data["password_hash"] = get_password_hash(data.password)

        if not user_data:
            return await self.get_by_id(entity_id, session)

        # Check uniqueness
        await self._check_unique_constraints(user_data, session, entity_id)

        # Update user
        user = await self.user_repo.update(entity_id, user_data, session)
        return self.read_schema.model_validate(user)

    async def authenticate(
        self, username: str, password: str, session: AsyncSession
    ) -> dict[str, Any]:
        """Authenticate user and return tokens."""
        logger.info(
            "authenticate() username=%r password_len=%d", username, len(password)
        )
        # Get user by username
        user = await self.user_repo.get_by_username(username, session)
        logger.info(f"DEBUG: User found: {user is not None}")
        if not user:
            raise AuthenticationError("Invalid username or password")

        # Check if user is active
        if not user.is_active:
            raise AuthenticationError("User account is inactive")

        # Verify password
        logger.info(f"DEBUG: Verifying password for user '{username}'")
        logger.info(
            f"DEBUG: Password length: {len(password)}, first 5 chars: '{password[:5]}'"
        )
        logger.info(f"DEBUG: Hash preview: '{user.password_hash[:30]}'")
        password_valid = verify_password(password, user.password_hash)
        logger.info(f"DEBUG: Password valid: {password_valid}")
        if not password_valid:
            raise AuthenticationError("Invalid username or password")

        # Generate tokens
        access_token = create_access_token(
            {"sub": str(user.id), "username": user.username}
        )
        refresh_token = create_refresh_token({"sub": str(user.id)})

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": self.read_schema.model_validate(user),
        }

    async def get_by_username(self, username: str, session: AsyncSession) -> UserRead:
        """Get user by username."""
        user = await self.user_repo.get_by_username(username, session)
        if not user:
            raise NotFoundError("User", username)  # type: ignore
        return self.read_schema.model_validate(user)

    async def get_by_email(self, email: str, session: AsyncSession) -> UserRead:
        """Get user by email."""
        user = await self.user_repo.get_by_email(email, session)
        if not user:
            raise NotFoundError("User", email)  # type: ignore
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
