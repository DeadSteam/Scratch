"""Security utilities: password hashing and JWT token management.

This module is HTTP-independent — it raises domain exceptions,
not HTTPException. The HTTP layer (dependencies.py) catches and converts them.
"""

from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
import jwt
from jwt.exceptions import PyJWTError

from .config import settings

# Bcrypt accepts at most 72 bytes; truncate to avoid ValueError with bcrypt 4+
BCRYPT_MAX_PASSWORD_BYTES = 72


class TokenValidationError(Exception):
    """Raised when JWT token validation fails."""

    def __init__(self, message: str = "Could not validate credentials"):
        self.message = message
        super().__init__(message)


def _password_bytes(password: str) -> bytes:
    """Return password as bytes, truncated to 72 bytes for bcrypt."""
    return password.encode("utf-8")[:BCRYPT_MAX_PASSWORD_BYTES]


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    secret = _password_bytes(plain_password)
    return bcrypt.checkpw(secret, hashed_password.encode("utf-8"))


def get_password_hash(password: str) -> str:
    """Generate password hash."""
    secret = _password_bytes(password)
    hashed = bcrypt.hashpw(secret, bcrypt.gensalt())
    return hashed.decode("utf-8")


def create_access_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    """Create JWT access token."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )


def create_refresh_token(data: dict[str, Any]) -> str:
    """Create JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )


def verify_token(token: str) -> dict[str, Any]:
    """Verify and decode JWT token.

    Raises:
        TokenValidationError: If the token is invalid or expired.
    """
    try:
        return jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
    except PyJWTError as err:
        raise TokenValidationError("Could not validate credentials") from err


def verify_refresh_token(token: str) -> dict[str, Any]:
    """Verify refresh token.

    Raises:
        TokenValidationError: If the token is invalid or not a refresh token.
    """
    payload = verify_token(token)
    if payload.get("type") != "refresh":
        raise TokenValidationError("Invalid token type")
    return payload
