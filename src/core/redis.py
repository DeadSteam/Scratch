"""Redis client wrapper with circuit breaker, error handling, and JSON serialization."""

import datetime
import json
import re
import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any, cast

import redis.asyncio as aioredis

from .circuit_breaker import CircuitOpenError, get_circuit_breaker
from .config import settings
from .logging_config import get_logger


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
    r"^\d{4}-\d{2}-\d{2}"
    r"(T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})?)?$"
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
    """Redis client wrapper with circuit breaker and proper error handling."""

    def __init__(
        self,
        url: str,
        encoding: str = "utf-8",
        decode_responses: bool = True,
    ) -> None:
        self._logger = get_logger(__name__)
        self.client = aioredis.from_url(
            url,
            encoding=encoding,
            decode_responses=decode_responses,
        )
        self.default_timeout = settings.REDIS_DEFAULT_TIMEOUT
        self._cb = get_circuit_breaker(
            "redis",
            failure_threshold=5,
            recovery_timeout=30.0,
            success_threshold=2,
        )

    async def set(
        self, key: str, value: Any, expire: int | None = None
    ) -> bool:
        """Set value in Redis with optional expiration."""
        try:
            self._cb.ensure_closed()
        except CircuitOpenError:
            self._logger.debug("redis_set_circuit_open", key=key)
            return False

        try:
            if not isinstance(value, (str, int, float, bool)):
                to_store: str | int | float = json.dumps(
                    value, cls=CustomJSONEncoder
                )
            else:
                to_store = value

            if expire is None:
                expire = self.default_timeout

            result = await self.client.set(key, to_store, ex=expire)
            self._cb.record_success()
            self._logger.debug("redis_set", key=key, expire=expire)
            return cast(bool, result) if result is not None else False
        except Exception as exc:
            self._cb.record_failure()
            self._logger.warning(
                "redis_set_failed", key=key, error=str(exc)
            )
            return False

    async def get(self, key: str) -> Any | None:
        """Get value from Redis with automatic deserialization."""
        try:
            self._cb.ensure_closed()
        except CircuitOpenError:
            self._logger.debug("redis_get_circuit_open", key=key)
            return None

        try:
            value = await self.client.get(key)
            if value is None:
                self._logger.debug("redis_get_miss", key=key)
                self._cb.record_success()
                return None

            self._cb.record_success()

            # Try to deserialize JSON
            try:
                if isinstance(value, str) and (
                    value.startswith("{") or value.startswith("[")
                ):
                    decoded = parse_json_with_dates(value)
                    self._logger.debug(
                        "redis_get_hit", key=key, decoded_json=True
                    )
                    return decoded
                self._logger.debug(
                    "redis_get_hit", key=key, decoded_json=False
                )
                return value
            except (TypeError, json.JSONDecodeError):
                self._logger.debug(
                    "redis_get_deserialize_failed", key=key
                )
                return value
        except Exception as exc:
            self._cb.record_failure()
            self._logger.warning(
                "redis_get_failed", key=key, error=str(exc)
            )
            return None

    async def delete(self, key: str) -> bool:
        """Delete key from Redis."""
        try:
            self._cb.ensure_closed()
        except CircuitOpenError:
            return False

        try:
            result = await self.client.delete(key)
            self._cb.record_success()
            deleted = cast(int, result) > 0
            self._logger.debug("redis_delete", key=key, deleted=deleted)
            return deleted
        except Exception as exc:
            self._cb.record_failure()
            self._logger.warning(
                "redis_delete_failed", key=key, error=str(exc)
            )
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """Delete keys matching pattern using SCAN."""
        try:
            self._cb.ensure_closed()
        except CircuitOpenError:
            return 0

        try:
            count = 0
            async for key in self.client.scan_iter(match=pattern):
                await self.client.delete(key)
                count += 1
            self._cb.record_success()
            self._logger.debug(
                "redis_delete_pattern", pattern=pattern, count=count
            )
            return count
        except Exception as exc:
            self._cb.record_failure()
            self._logger.warning(
                "redis_delete_pattern_failed",
                pattern=pattern,
                error=str(exc),
            )
            return 0

    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        try:
            self._cb.ensure_closed()
        except CircuitOpenError:
            return False

        try:
            result = await self.client.exists(key) > 0
            self._cb.record_success()
            self._logger.debug("redis_exists", key=key, exists=result)
            return cast(bool, result)
        except Exception as exc:
            self._cb.record_failure()
            self._logger.warning(
                "redis_exists_failed", key=key, error=str(exc)
            )
            return False

    async def ping(self) -> bool:
        """Ping Redis to check connectivity."""
        try:
            return bool(await self.client.ping())
        except Exception:
            return False

    async def close(self) -> None:
        """Close Redis connection."""
        self._logger.info("redis_client_close")
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
