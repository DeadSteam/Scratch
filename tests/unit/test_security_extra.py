"""Extra coverage for security tokens beyond type-separation:

* S15: secondary-key rotation (verify_token tries each key in order).
* S16: ALGORITHM whitelist (none/junk rejected at Settings load).
* Refresh-token `family` claim (S11 prereq).
"""

from __future__ import annotations

import jwt as pyjwt
import pytest
from pydantic import ValidationError

from src.core.config import Settings, settings
from src.core.security import (
    TokenValidationError,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    verify_token,
)


def test_refresh_token_has_family_claim():
    """S11 prerequisite: every refresh token carries a `family` UUID."""
    token = create_refresh_token({"sub": "user-1"})
    payload = verify_refresh_token(token)
    assert "family" in payload
    assert len(payload["family"]) >= 32  # UUID hex


def test_refresh_token_explicit_family_preserved():
    """Rotation preserves family across new tokens."""
    family = "00000000-0000-0000-0000-deadbeefdead"
    token = create_refresh_token({"sub": "user-1"}, family_id=family)
    payload = verify_refresh_token(token)
    assert payload["family"] == family


def test_verify_token_accepts_secondary_key(monkeypatch):
    """S15: a token signed with a key in SECONDARY_SECRET_KEYS still verifies.

    We patch the live Settings instance directly because security.py imports
    `settings` at module load time (not via get_settings()).
    """
    old_key = "rotated-out-but-still-valid-key-32-characters-long"
    monkeypatch.setattr(
        settings,
        "SECONDARY_SECRET_KEYS",
        [old_key],
    )

    token_signed_with_old = pyjwt.encode(
        {
            "sub": "u",
            "type": "access",
            "iss": settings.JWT_ISSUER,
            "aud": settings.JWT_AUDIENCE,
        },
        old_key,
        algorithm=settings.ALGORITHM,
    )
    payload = verify_token(token_signed_with_old)
    assert payload["sub"] == "u"


def test_verify_token_rejects_unknown_key(monkeypatch):
    """Token signed with a key NOT in the rotation list must be rejected."""
    monkeypatch.setattr(settings, "SECONDARY_SECRET_KEYS", [])

    foreign = pyjwt.encode(
        {
            "sub": "u",
            "type": "access",
            "iss": settings.JWT_ISSUER,
            "aud": settings.JWT_AUDIENCE,
        },
        "totally-unrelated-key-at-least-32-characters-long",
        algorithm=settings.ALGORITHM,
    )
    with pytest.raises(TokenValidationError):
        verify_token(foreign)


def test_algorithm_whitelist_rejects_none(monkeypatch):
    """S16: ENV ALGORITHM=none must fail at Settings load (signature bypass)."""
    monkeypatch.setenv("ALGORITHM", "none")
    with pytest.raises(ValidationError):
        Settings()


def test_algorithm_whitelist_rejects_garbage(monkeypatch):
    monkeypatch.setenv("ALGORITHM", "MD5")
    with pytest.raises(ValidationError):
        Settings()


def test_access_token_jti_is_unique():
    """Two tokens minted back-to-back have different `jti`s — required for
    granular revocation (S6)."""
    t1 = create_access_token({"sub": "u"})
    t2 = create_access_token({"sub": "u"})
    p1, p2 = verify_token(t1), verify_token(t2)
    assert p1["jti"] != p2["jti"]
