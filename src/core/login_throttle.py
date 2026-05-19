"""Per-username login throttle.

Layered on top of slowapi's per-IP limit. The IP limit stops single-host
brute-force; this one stops distributed (botnet) brute-force against a
specific account.

Each failed authentication increments `login_fail:<username>` in Redis. When
the counter exceeds the threshold, further attempts are rejected for the
duration of the window — regardless of source IP.
"""

from __future__ import annotations

from .config import settings  # noqa: F401  (kept for future tunable thresholds)
from .redis import get_redis_client

_PREFIX = "login_fail:"

# Window and threshold. Tunable; not put into settings to keep the surface
# small. 10 failures in 15 minutes is conservative enough for humans, harsh
# enough for spray attackers.
WINDOW_SECONDS = 15 * 60
THRESHOLD = 10


def _key(username: str) -> str:
    return f"{_PREFIX}{username.lower().strip()}"


async def is_login_locked(username: str) -> bool:
    """Return True if this username is currently rate-limited."""
    client = await get_redis_client()
    value = await client.get(_key(username))
    if value is None:
        return False
    try:
        count = int(value)
    except (TypeError, ValueError):
        return False
    return count >= THRESHOLD


async def record_login_failure(username: str) -> int:
    """Increment failure counter (and seed TTL on first hit). Returns new value."""
    client = await get_redis_client()
    key = _key(username)
    # incr returns the new value; we set TTL on first hit only.
    raw = await client.client.incr(key)
    if raw == 1:
        await client.client.expire(key, WINDOW_SECONDS)
    return int(raw)


async def reset_login_failures(username: str) -> None:
    """Clear failure counter on successful login."""
    client = await get_redis_client()
    await client.delete(_key(username))
