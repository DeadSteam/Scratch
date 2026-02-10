"""Authentication service.

Responsible for user authentication and JWT token management.
Follows SRP — separated from UserService which handles CRUD operations.
"""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from ..core.logging_config import get_logger
from ..core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
)
from ..repositories.user_repository import UserRepository
from ..schemas.user import UserRead
from .exceptions import AuthenticationError

logger = get_logger("service.auth")


class AuthService:
    """Service for authentication and token management."""

    def __init__(self, user_repository: UserRepository):
        self._user_repo = user_repository
        self._logger = logger

    async def authenticate(
        self, username: str, password: str, session: AsyncSession
    ) -> dict[str, Any]:
        """Authenticate user by credentials and return JWT tokens.

        Raises:
            AuthenticationError: If credentials are invalid or user is inactive.
        """
        self._logger.info("authentication_attempt", username=username)

        user = await self._user_repo.get_by_username(username, session)
        if not user:
            self._logger.warning("authentication_failed", reason="user_not_found")
            raise AuthenticationError("Invalid username or password")

        if not user.is_active:
            self._logger.warning(
                "authentication_failed", reason="user_inactive", username=username
            )
            raise AuthenticationError("User account is inactive")

        if not verify_password(password, user.password_hash):
            self._logger.warning(
                "authentication_failed", reason="invalid_password", username=username
            )
            raise AuthenticationError("Invalid username or password")

        access_token = create_access_token(
            {"sub": str(user.id), "username": user.username}
        )
        refresh_token = create_refresh_token({"sub": str(user.id)})

        self._logger.info("authentication_success", username=username)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": UserRead.model_validate(user),
        }
