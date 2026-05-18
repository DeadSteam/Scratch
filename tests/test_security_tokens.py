"""JWT access/refresh token type separation."""

import pytest

from src.core.security import (
    TokenValidationError,
    create_access_token,
    create_refresh_token,
    verify_access_token,
    verify_refresh_token,
)


def test_access_token_has_access_type():
    token = create_access_token({"sub": "user-1"})
    payload = verify_access_token(token)
    assert payload["type"] == "access"
    assert payload.get("jti")


def test_refresh_token_rejected_as_access():
    token = create_refresh_token({"sub": "user-1"})
    with pytest.raises(TokenValidationError, match="Invalid token type"):
        verify_access_token(token)


def test_refresh_token_verification():
    token = create_refresh_token({"sub": "user-1"})
    payload = verify_refresh_token(token)
    assert payload["type"] == "refresh"
