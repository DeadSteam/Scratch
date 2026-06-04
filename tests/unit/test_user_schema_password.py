"""Password policy regression (Pydantic schema-level)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.schemas.user import UserCreate


def _payload(password: str) -> dict:
    return {
        "username": "alice",
        "email": "alice@example.com",
        "password": password,
    }


def test_password_too_short_rejected():
    with pytest.raises(ValidationError) as exc:
        UserCreate.model_validate(_payload("Aa1abcd"))  # 7 chars
    assert "at least 8" in str(exc.value).lower()


def test_password_no_uppercase_rejected():
    with pytest.raises(ValidationError):
        UserCreate.model_validate(_payload("password123"))


def test_password_no_lowercase_rejected():
    with pytest.raises(ValidationError):
        UserCreate.model_validate(_payload("PASSWORD123"))


def test_password_no_digit_rejected():
    with pytest.raises(ValidationError):
        UserCreate.model_validate(_payload("Passwordpass"))


def test_password_valid_accepted():
    u = UserCreate.model_validate(_payload("Password1"))
    assert u.password == "Password1"


def test_username_alphanumeric_lowercased():
    """Mixed-case username is lowercased; punctuation rejected."""
    u = UserCreate.model_validate(_payload("Password1") | {"username": "Alice_42"})
    assert u.username == "alice_42"

    with pytest.raises(ValidationError):
        UserCreate.model_validate(_payload("Password1") | {"username": "alice!42"})
