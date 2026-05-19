"""Authentication service.

Responsible for user authentication and JWT token management.
Follows SRP — separated from UserService which handles CRUD operations.
"""

import hashlib
from typing import Any
from uuid import UUID

import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.audit import emit_audit_event
from ..core.logging_config import get_logger
from ..core.login_throttle import (
    is_login_locked,
    record_login_failure,
    reset_login_failures,
)
from ..core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
)
from ..core.token_store import (
    blacklist_refresh_token,
    is_refresh_family_revoked,
    is_refresh_token_blacklisted,
    revoke_refresh_family,
)
from ..repositories.user_repository import UserRepository
from ..schemas.user import UserRead
from .exceptions import AuthenticationError

# A pre-computed bcrypt hash used to keep timing constant when the username
# does not exist (otherwise the absent verify_password call is a side channel).
_DUMMY_HASH = bcrypt.hashpw(b"dummy", bcrypt.gensalt()).decode("utf-8")
_GENERIC_AUTH_ERROR = "Invalid username or password"


def _hash_username(username: str) -> str:
    """Return a short, non-reversible identifier for log correlation.

    SECURITY (S17): we still want to correlate audit/log entries for the
    same login session, but we don't want the raw username (potential PII)
    persisted to log aggregation. SHA-256 truncated to 12 hex chars is
    enough to detect repeated failures without enabling enumeration.
    """
    return hashlib.sha256(username.strip().lower().encode("utf-8")).hexdigest()[:12]


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

        SECURITY: keeps the response uniform across all failure modes
        (no user / inactive / bad password) to prevent username enumeration
        and timing-based side channels.

        Raises:
            AuthenticationError: If credentials are invalid or user is inactive.
        """
        # Use a non-reversible hash for log entries (S17). Audit channel
        # is allowed to receive the real user_id where authentication
        # succeeded; pre-auth logs only carry the hash.
        log_uname = _hash_username(username)
        self._logger.info("authentication_attempt", username_hash=log_uname)

        # SECURITY: per-username lockout — guards against distributed brute-force
        # that bypasses the slowapi per-IP limit.
        if await is_login_locked(username):
            self._logger.warning(
                "authentication_locked",
                username_hash=log_uname,
                reason="too_many_failures",
            )
            raise AuthenticationError("Too many failed attempts. Try again later.")

        user = await self._user_repo.get_by_username(username, session)
        if not user:
            # Run a dummy bcrypt verify so attackers can't tell user-not-found
            # from bad-password via response timing.
            verify_password(password, _DUMMY_HASH)
            await record_login_failure(username)
            self._logger.warning(
                "authentication_failed",
                reason="user_not_found",
                username_hash=log_uname,
            )
            raise AuthenticationError(_GENERIC_AUTH_ERROR)

        if not verify_password(password, user.password_hash):
            await record_login_failure(username)
            self._logger.warning(
                "authentication_failed",
                reason="invalid_password",
                username_hash=log_uname,
            )
            raise AuthenticationError(_GENERIC_AUTH_ERROR)

        if not user.is_active:
            await record_login_failure(username)
            self._logger.warning(
                "authentication_failed",
                reason="user_inactive",
                username_hash=log_uname,
            )
            # Generic error: never reveal account state.
            raise AuthenticationError(_GENERIC_AUTH_ERROR)

        access_token = create_access_token(
            {"sub": str(user.id), "username": user.username}
        )
        refresh_token = create_refresh_token({"sub": str(user.id)})

        await reset_login_failures(username)
        self._logger.info(
            "authentication_success",
            username_hash=log_uname,
            user_id=str(user.id),
        )
        emit_audit_event(
            user_id=str(user.id),
            action="LOGIN",
            resource="/auth/login",
            details={"username_hash": log_uname},
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": UserRead.model_validate(user),
        }

    async def refresh(
        self,
        payload: dict[str, Any],
        session: AsyncSession,
        *,
        previous_refresh_token: str | None = None,
    ) -> dict[str, Any]:
        """Issue new tokens from a valid refresh token payload.

        SECURITY (S11): refresh tokens carry a `family` id. When a token
        is rotated, the previous one is blacklisted. If an attacker later
        replays that blacklisted token, the *entire family* is revoked —
        the legit user loses their session, but more importantly the
        thief loses theirs too. Re-login required.

        Raises:
            AuthenticationError: If the token is replayed, the family is
                revoked, or the user is missing/inactive.
        """
        family_id = payload.get("family")

        # Family burned by a prior theft detection? Reject before doing
        # anything else.
        if await is_refresh_family_revoked(family_id):
            self._logger.warning(
                "refresh_rejected_family_revoked", family=family_id
            )
            raise AuthenticationError("Refresh token has been revoked")

        if previous_refresh_token:
            if await is_refresh_token_blacklisted(previous_refresh_token):
                # Replay of a rotated token == possible theft. Burn the
                # whole family.
                self._logger.warning(
                    "refresh_token_replay_detected", family=family_id
                )
                if family_id:
                    await revoke_refresh_family(family_id)
                raise AuthenticationError("Refresh token has been revoked")
            exp = payload.get("exp")
            if isinstance(exp, int):
                await blacklist_refresh_token(previous_refresh_token, exp)

        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise AuthenticationError("Invalid refresh token")

        try:
            user_id = UUID(user_id_str)
        except ValueError as exc:
            raise AuthenticationError("Invalid user ID in token") from exc

        user = await self._user_repo.get_by_id(user_id, session)
        if not user or not user.is_active:
            raise AuthenticationError("Invalid refresh token")

        access_token = create_access_token(
            {"sub": str(user.id), "username": user.username}
        )
        # Preserve the family across rotation — only a fresh /auth/login
        # mints a new family.
        new_refresh_token = create_refresh_token(
            {"sub": str(user.id)}, family_id=family_id
        )

        self._logger.info("token_refreshed", user_id=str(user.id), family=family_id)

        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "user": UserRead.model_validate(user),
        }
