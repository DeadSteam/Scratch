import datetime
import json
import re
import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any, cast

import redis.asyncio as aioredis

from .config import settings


class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for handling UUID and datetime objects."""

    def default(self, o: Any) -> Any:
        if isinstance(o, uuid.UUID):
            return str(o)
        elif isinstance(o, (datetime.datetime, datetime.date)):
            return o.isoformat()
        elif isinstance(o, datetime.timedelta):
            return o.total_seconds()
        return super().default(o)


# Regex for ISO date format detection
ISO_DATE_REGEX = re.compile(
    r"^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})?)?$"
)


def parse_json_with_dates(json_str: str) -> Any:
    """Parse JSON string with automatic datetime conversion."""

    def object_hook(obj: dict[str, Any]) -> dict[str, Any]:
        for key, value in obj.items():
            if isinstance(value, str) and ISO_DATE_REGEX.match(value):
                try:
                    if "T" in value:
                        obj[key] = datetime.datetime.fromisoformat(
                            value.replace("Z", "+00:00")
                        )
                    else:
                        obj[key] = datetime.date.fromisoformat(value)
                except (ValueError, TypeError):
                    pass
        return obj

    return json.loads(json_str, object_hook=object_hook)


class RedisClient:
    """Redis client wrapper with proper error handling and serialization."""

    def __init__(
        self, url: str, encoding: str = "utf-8", decode_responses: bool = True
    ) -> None:
        self.client = aioredis.from_url(
            url,
            encoding=encoding,
            decode_responses=decode_responses,
        )
        self.default_timeout = settings.REDIS_DEFAULT_TIMEOUT

    async def set(self, key: str, value: Any, expire: int | None = None) -> bool:
        """Set value in Redis with optional expiration."""
        try:
            if not isinstance(value, (str, int, float, bool)):
                to_store: str | int | float = json.dumps(value, cls=CustomJSONEncoder)
            else:
                to_store = value

            if expire is None:
                expire = self.default_timeout

            result = await self.client.set(key, to_store, ex=expire)
            return cast(bool, result) if result is not None else False
        except Exception:
            return False

    async def get(self, key: str) -> Any | None:
        """Get value from Redis with automatic deserialization."""
        try:
            value = await self.client.get(key)
            if value is None:
                return None

            # Try to deserialize JSON
            try:
                if isinstance(value, str) and (
                    value.startswith("{") or value.startswith("[")
                ):
                    return parse_json_with_dates(value)
                return value
            except (TypeError, json.JSONDecodeError):
                return value
        except Exception:
            # print(f"Redis get error for key '{key}': {e}")
            return None

    async def delete(self, key: str) -> bool:
        """Delete key from Redis."""
        try:
            result = await self.client.delete(key) > 0
            return cast(bool, result)
        except Exception:
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        try:
            result = await self.client.exists(key) > 0
            return cast(bool, result)
        except Exception:
            return False

    async def close(self) -> None:
        """Close Redis connection."""
        await self.client.close()


# Global Redis client instance
_redis_client: RedisClient | None = None


async def get_redis_client() -> RedisClient:
    """Get Redis client instance (singleton)."""
    global _redis_client
    if _redis_client is None:
        _redis_client = RedisClient(settings.REDIS_URL)
    return _redis_client


async def close_redis_connection() -> None:
    """Close Redis connection."""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None


@asynccontextmanager
async def redis_transaction() -> AsyncGenerator["RedisClient"]:
    """Context manager for Redis operations."""
    client = await get_redis_client()
    try:
        yield client
    finally:
        pass  # Don't close the global client here
