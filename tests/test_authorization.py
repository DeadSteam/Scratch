"""Unit tests for resource authorization helpers."""

from uuid import uuid4

import pytest

from src.core.authorization import ensure_same_user_or_admin, is_admin
from src.schemas.user import RoleRead, UserRead
from src.services.exceptions import AuthorizationError


def _user(user_id=None, roles=None) -> UserRead:
    return UserRead(
        id=user_id or uuid4(),
        username="tester",
        email="tester@example.com",
        is_active=True,
        roles=roles or [],
    )


def test_is_admin_with_admin_role():
    user = _user(roles=[RoleRead(id=uuid4(), name="admin")])
    assert is_admin(user) is True


def test_is_admin_without_admin_role():
    user = _user(roles=[RoleRead(id=uuid4(), name="user")])
    assert is_admin(user) is False


def test_ensure_same_user_or_admin_owner():
    user_id = uuid4()
    user = _user(user_id=user_id)
    ensure_same_user_or_admin(user, user_id)


def test_ensure_same_user_or_admin_forbidden():
    user = _user()
    with pytest.raises(AuthorizationError):
        ensure_same_user_or_admin(user, uuid4())
