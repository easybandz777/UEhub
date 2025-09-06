"""
Redis cache service adapter.
"""

import json
import logging
from typing import Optional

import redis.asyncio as redis
from redis.asyncio import Redis

from ..core.interfaces import CacheService

logger = logging.getLogger(__name__)


class RedisCacheService:
    """Redis implementation of cache service."""
    
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self._redis: Optional[Redis] = None
    
    async def _get_redis(self) -> Redis:
        """Get Redis connection."""
        if self._redis is None:
            self._redis = redis.from_url(self.redis_url)
        return self._redis
    
    async def get(self, key: str) -> Optional[str]:
        """Get a value from cache."""
        try:
            redis_client = await self._get_redis()
            value = await redis_client.get(key)
            return value.decode() if value else None
        except Exception as e:
            logger.error(f"Cache get error for key '{key}': {e}")
            return None
    
    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        """Set a value in cache with optional TTL."""
        try:
            redis_client = await self._get_redis()
            await redis_client.set(key, value, ex=ttl)
        except Exception as e:
            logger.error(f"Cache set error for key '{key}': {e}")
    
    async def delete(self, key: str) -> None:
        """Delete a key from cache."""
        try:
            redis_client = await self._get_redis()
            await redis_client.delete(key)
        except Exception as e:
            logger.error(f"Cache delete error for key '{key}': {e}")
    
    async def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        try:
            redis_client = await self._get_redis()
            result = await redis_client.exists(key)
            return bool(result)
        except Exception as e:
            logger.error(f"Cache exists error for key '{key}': {e}")
            return False
    
    async def get_json(self, key: str) -> Optional[dict]:
        """Get and deserialize JSON value from cache."""
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error for key '{key}': {e}")
        return None
    
    async def set_json(self, key: str, value: dict, ttl: Optional[int] = None) -> None:
        """Serialize and set JSON value in cache."""
        try:
            json_value = json.dumps(value)
            await self.set(key, json_value, ttl)
        except (TypeError, ValueError) as e:
            logger.error(f"JSON encode error for key '{key}': {e}")
    
    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment a numeric value in cache."""
        try:
            redis_client = await self._get_redis()
            return await redis_client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Cache increment error for key '{key}': {e}")
            return 0
    
    async def close(self) -> None:
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
