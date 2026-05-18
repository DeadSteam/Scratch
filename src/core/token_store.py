"""Refresh token revocation via Redis."""

import hashlib
import time

from .redis import get_redis_client

_REFRESH_PREFIX = "refresh_blacklist:"


def _token_key(token: str) -> str:
    digest = hashlib.sha256(token.encode()).hexdigest()
    return f"{_REFRESH_PREFIX}{digest}"


async def blacklist_refresh_token(token: str, exp_timestamp: int) -> None:
    """Store a refresh token hash until its natural expiry."""
    ttl = max(int(exp_timestamp) - int(time.time()), 1)
    client = await get_redis_client()
    await client.set(_token_key(token), "1", expire=ttl)


async def is_refresh_token_blacklisted(token: str) -> bool:
    """Return True if the refresh token was revoked."""
    client = await get_redis_client()
    return bool(await client.exists(_token_key(token)))
