from typing import Any, Optional
import redis.asyncio as aioredis
import json
import uuid
import datetime
import re
from contextlib import asynccontextmanager

from .config import settings


class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for handling UUID and datetime objects."""
    
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)
        elif isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        elif isinstance(obj, datetime.timedelta):
            return obj.total_seconds()
        return super().default(obj)


# Regex for ISO date format detection
ISO_DATE_REGEX = re.compile(r'^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})?)?$')


def parse_json_with_dates(json_str: str) -> Any:
    """Parse JSON string with automatic datetime conversion."""
    def object_hook(obj):
        for key, value in obj.items():
            if isinstance(value, str) and ISO_DATE_REGEX.match(value):
                try:
                    if 'T' in value:
                        obj[key] = datetime.datetime.fromisoformat(value.replace('Z', '+00:00'))
                    else:
                        obj[key] = datetime.date.fromisoformat(value)
                except (ValueError, TypeError):
                    pass
        return obj
    
    return json.loads(json_str, object_hook=object_hook)


class RedisClient:
    """Redis client wrapper with proper error handling and serialization."""
    
    def __init__(self, url: str, encoding: str = "utf-8", decode_responses: bool = True):
        self.client = aioredis.from_url(
            url,
            encoding=encoding,
            decode_responses=decode_responses,
        )
        self.default_timeout = settings.REDIS_DEFAULT_TIMEOUT
    
    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Set value in Redis with optional expiration."""
        try:
            if not isinstance(value, (str, int, float, bool)):
                serialized_value = json.dumps(value, cls=CustomJSONEncoder)
            else:
                serialized_value = value
            
            if expire is None:
                expire = self.default_timeout
            
            result = await self.client.set(key, serialized_value, ex=expire)
            return result
        except Exception as e:
            # print(f"Redis set error for key '{key}': {e}")
            return False
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis with automatic deserialization."""
        try:
            value = await self.client.get(key)
            if value is None:
                return None
            
            # Try to deserialize JSON
            try:
                if isinstance(value, str) and (value.startswith('{') or value.startswith('[')):
                    return parse_json_with_dates(value)
                return value
            except (TypeError, json.JSONDecodeError):
                return value
        except Exception as e:
            # print(f"Redis get error for key '{key}': {e}")
            return None
    
    async def delete(self, key: str) -> bool:
        """Delete key from Redis."""
        try:
            result = await self.client.delete(key) > 0
            return result
        except Exception as e:
            # print(f"Redis delete error for key '{key}': {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        try:
            result = await self.client.exists(key) > 0
            return result
        except Exception as e:
            # print(f"Redis exists error for key '{key}': {e}")
            return False
    
    async def close(self):
        """Close Redis connection."""
        await self.client.close()


# Global Redis client instance
_redis_client: Optional[RedisClient] = None


async def get_redis_client() -> RedisClient:
    """Get Redis client instance (singleton)."""
    global _redis_client
    if _redis_client is None:
        _redis_client = RedisClient(settings.REDIS_URL)
    return _redis_client


async def close_redis_connection():
    """Close Redis connection."""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None


@asynccontextmanager
async def redis_transaction():
    """Context manager for Redis operations."""
    client = await get_redis_client()
    try:
        yield client
    finally:
        pass  # Don't close the global client here
