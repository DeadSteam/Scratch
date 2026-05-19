"""Token revocation via Redis.

- Refresh tokens are blacklisted by hashing the token string (clients submit
  the token; we never see its plaintext after issue).
- Access tokens are blacklisted by their `jti` claim, set in security.py.
  The JWT signature is already verified before we look up the JTI, so this
  is cheap (one Redis GET per request).
"""

import hashlib
import time

from .redis import get_redis_client

_REFRESH_PREFIX = "refresh_blacklist:"
_ACCESS_PREFIX = "access_blacklist:"
_FAMILY_PREFIX = "refresh_family_revoked:"

# When a refresh-token family is burned (theft detected), the marker lives
# for at least this long so any in-flight tokens from the family are rejected.
_FAMILY_TTL_SECONDS = 30 * 24 * 3600  # 30 days


def _refresh_key(token: str) -> str:
    digest = hashlib.sha256(token.encode()).hexdigest()
    return f"{_REFRESH_PREFIX}{digest}"


def _access_key(jti: str) -> str:
    return f"{_ACCESS_PREFIX}{jti}"


def _ttl_until(exp_timestamp: int | float | None) -> int:
    if exp_timestamp is None:
        # If we can't read exp, default to 1h so the key doesn't live forever.
        return 3600
    return max(int(exp_timestamp) - int(time.time()), 1)


async def blacklist_refresh_token(token: str, exp_timestamp: int) -> None:
    """Store a refresh token hash until its natural expiry."""
    client = await get_redis_client()
    await client.set(_refresh_key(token), "1", expire=_ttl_until(exp_timestamp))


async def is_refresh_token_blacklisted(token: str) -> bool:
    """Return True if the refresh token was revoked."""
    client = await get_redis_client()
    return bool(await client.exists(_refresh_key(token)))


async def blacklist_access_jti(jti: str, exp_timestamp: int | float | None) -> None:
    """Revoke an access token by its JTI. Used on logout and password change."""
    client = await get_redis_client()
    await client.set(_access_key(jti), "1", expire=_ttl_until(exp_timestamp))


async def is_access_jti_blacklisted(jti: str) -> bool:
    """Check if an access token JTI has been revoked."""
    client = await get_redis_client()
    return bool(await client.exists(_access_key(jti)))


# ---------------------------------------------------------------------------
# Refresh-token family revocation (S11: theft detection)
# ---------------------------------------------------------------------------
def _family_key(family_id: str) -> str:
    return f"{_FAMILY_PREFIX}{family_id}"


async def revoke_refresh_family(family_id: str) -> None:
    """Burn every refresh token in the same family.

    Called when a previously-rotated refresh token is replayed — that's a
    strong signal of theft, so we invalidate the entire chain (the legit
    user will be forced to log in again, which is the right outcome).
    """
    if not family_id:
        return
    client = await get_redis_client()
    await client.set(_family_key(family_id), "1", expire=_FAMILY_TTL_SECONDS)


async def is_refresh_family_revoked(family_id: str | None) -> bool:
    """Return True if any token in this family has been revoked."""
    if not family_id:
        return False
    client = await get_redis_client()
    return bool(await client.exists(_family_key(family_id)))
