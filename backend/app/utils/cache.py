"""Redis caching utilities."""
import json
from datetime import timedelta
from typing import Any, Optional, Callable, Awaitable
from functools import wraps

from redis.asyncio import Redis
from redis.asyncio.connection import ConnectionPool

from app.core.config import settings


class Cache:
    """Redis-based caching with JSON serialization."""

    def __init__(self, redis_url: str = settings.redis_url):
        self.redis_url = redis_url
        self.pool = None
        self.redis = None

    async def connect(self):
        """Initialize Redis connection."""
        if not self.redis:
            self.pool = ConnectionPool.from_url(self.redis_url)
            self.redis = Redis(connection_pool=self.pool)

    async def disconnect(self):
        """Close Redis connection."""
        if self.redis:
            await self.redis.close()
            self.redis = None
        if self.pool:
            await self.pool.disconnect()
            self.pool = None

    async def get(self, key: str) -> Any | None:
        """Get a value from cache."""
        if not self.redis:
            await self.connect()

        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
        except Exception:
            # Cache miss or error - continue without cache
            pass
        return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: timedelta | None = None
    ) -> bool:
        """Set a value in cache."""
        if not self.redis:
            await self.connect()

        try:
            serialized = json.dumps(value, default=str)
            if ttl:
                await self.redis.setex(key, int(ttl.total_seconds()), serialized)
            else:
                await self.redis.set(key, serialized)
            return True
        except Exception:
            # Cache write failed - continue without cache
            return False

    async def delete(self, key: str) -> bool:
        """Delete a key from cache."""
        if not self.redis:
            await self.connect()

        try:
            result = await self.redis.delete(key)
            return result > 0
        except Exception:
            return False

    async def clear_pattern(self, pattern: str) -> bool:
        """Clear all keys matching a pattern."""
        if not self.redis:
            await self.connect()

        try:
            keys = await self.redis.keys(pattern)
            if keys:
                await self.redis.delete(*keys)
            return True
        except Exception:
            return False


# Global cache instance
cache = Cache()


async def get_cache() -> Cache:
    """Get the global cache instance."""
    return cache


async def cache_get(key: str) -> Any | None:
    """Convenience function to get from cache."""
    return await cache.get(key)


async def cache_set(
    key: str,
    value: Any,
    ttl: timedelta | None = None
) -> bool:
    """Convenience function to set in cache."""
    return await cache.set(key, value, ttl)


async def cache_delete(key: str) -> bool:
    """Convenience function to delete from cache."""
    return await cache.delete(key)


def make_cache_key(*parts: str) -> str:
    """Create a cache key from parts."""
    return ":".join(str(part) for part in parts if part)


def cached(ttl: timedelta | None = None, key_prefix: str = ""):
    """Decorator to cache function results."""
    def decorator(func: Callable[..., Awaitable]):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = make_cache_key(key_prefix, func.__name__, *args, *kwargs.values())
            cache_key = cache_key.replace(" ", "_")  # Replace spaces with underscores

            # Try to get from cache first
            cached_result = await cache_get(cache_key)
            if cached_result is not None:
                return cached_result

            # Call the original function
            result = await func(*args, **kwargs)

            # Cache the result
            await cache_set(cache_key, result, ttl)

            return result
        return wrapper
    return decorator


def cache_invalidate(pattern: str):
    """Decorator to invalidate cache entries matching a pattern."""
    def decorator(func: Callable[..., Awaitable]):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)

            # Clear cache entries matching the pattern
            await cache.clear_pattern(pattern)

            return result
        return wrapper
    return decorator
