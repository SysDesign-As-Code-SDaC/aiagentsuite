"""
AI Agent Suite Caching Layer

Provides enterprise-grade caching with Redis support, memory caching,
TTL management, cache invalidation, and performance optimizations.
"""

import asyncio
import hashlib
import json
import time
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Dict, List, Optional, Set, Union, Callable, TypeVar, AsyncGenerator
import logging

import aiocache
from aiocache import Cache, serializers
from aiocache.plugins import HitMissRatioPlugin, TimingPlugin
import redis.asyncio as redis

from .config import get_global_config_manager
from .errors import get_global_error_handler, ResourceError
from .observability import get_global_observability_manager

logger = logging.getLogger(__name__)

T = TypeVar('T')


class CacheEntry:
    """Represents a cache entry with metadata."""

    def __init__(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        created_at: Optional[datetime] = None,
        access_count: int = 0,
        last_accessed: Optional[datetime] = None
    ):
        self.key = key
        self.value = value
        self.ttl = ttl
        self.created_at = created_at or datetime.now()
        self.access_count = access_count
        self.last_accessed = last_accessed

    def is_expired(self) -> bool:
        """Check if entry is expired."""
        if not self.ttl:
            return False
        return (datetime.now() - self.created_at).total_seconds() > self.ttl

    def access(self) -> None:
        """Record access to this entry."""
        self.access_count += 1
        self.last_accessed = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "key": self.key,
            "value": self.value,
            "ttl": self.ttl,
            "created_at": self.created_at.isoformat(),
            "access_count": self.access_count,
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CacheEntry':
        """Create from dictionary."""
        return cls(
            key=data["key"],
            value=data["value"],
            ttl=data["ttl"],
            created_at=datetime.fromisoformat(data["created_at"]),
            access_count=data.get("access_count", 0),
            last_accessed=datetime.fromisoformat(data["last_accessed"]) if data.get("last_accessed") else None
        )


class CacheStrategy(ABC):
    """Abstract base class for cache strategies."""

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        pass

    @abstractmethod
    async def clear(self) -> bool:
        """Clear all values from cache."""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        pass

    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        pass


class MemoryCache(CacheStrategy):
    """In-memory cache implementation."""

    def __init__(self, max_size: int = 1000):
        self.cache: Dict[str, CacheEntry] = {}
        self.max_size = max_size
        self._lock = asyncio.Lock()
        self._hits = 0
        self._misses = 0
        self._sets = 0
        self._deletes = 0

    async def get(self, key: str) -> Optional[Any]:
        """Get value from memory cache."""
        async with self._lock:
            entry = self.cache.get(key)
            if entry and not entry.is_expired():
                entry.access()
                self._hits += 1
                return entry.value
            else:
                if entry and entry.is_expired():
                    del self.cache[key]
                self._misses += 1
                return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in memory cache."""
        async with self._lock:
            # Evict if at max size (simple LRU-like eviction)
            if len(self.cache) >= self.max_size and key not in self.cache:
                # Remove least recently used item
                oldest_key = min(self.cache.keys(),
                               key=lambda k: self.cache[k].last_accessed or self.cache[k].created_at)
                del self.cache[oldest_key]

            self.cache[key] = CacheEntry(key, value, ttl)
            self._sets += 1
            return True

    async def delete(self, key: str) -> bool:
        """Delete value from memory cache."""
        async with self._lock:
            if key in self.cache:
                del self.cache[key]
                self._deletes += 1
                return True
            return False

    async def clear(self) -> bool:
        """Clear all values from memory cache."""
        async with self._lock:
            self.cache.clear()
            return True

    async def exists(self, key: str) -> bool:
        """Check if key exists in memory cache."""
        async with self._lock:
            entry = self.cache.get(key)
            return entry is not None and not entry.is_expired()

    def get_stats(self) -> Dict[str, Any]:
        """Get memory cache statistics."""
        return {
            "type": "memory",
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": self._hits / max(self._hits + self._misses, 1),
            "sets": self._sets,
            "deletes": self._deletes
        }


class RedisCache(CacheStrategy):
    """Redis cache implementation."""

    def __init__(self, url: str, pool_size: int = 10, ttl: int = 3600):
        self.url = url
        self.pool_size = pool_size
        self.default_ttl = ttl
        self.redis: Optional[redis.Redis] = None
        self._hits = 0
        self._misses = 0
        self._sets = 0
        self._deletes = 0
        self._connected = False

    async def _ensure_connection(self) -> None:
        """Ensure Redis connection is established."""
        if not self.redis or not self._connected:
            try:
                self.redis = redis.from_url(self.url, max_connections=self.pool_size)
                await self.redis.ping()
                self._connected = True
                logger.info("Redis cache connected successfully")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                self.redis = None
                self._connected = False
                raise ResourceError(f"Redis connection failed: {e}")

    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache."""
        try:
            await self._ensure_connection()
            if not self.redis:
                return None
            value = await self.redis.get(key)
            if value:
                # Try to deserialize JSON
                try:
                    value = json.loads(value.decode())
                except (json.JSONDecodeError, UnicodeDecodeError):
                    value = value.decode()

                self._hits += 1
                return value
            else:
                self._misses += 1
                return None
        except Exception as e:
            logger.warning(f"Redis get failed: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in Redis cache."""
        try:
            await self._ensure_connection()
            if not self.redis:
                return False

            # Serialize value
            if isinstance(value, (dict, list)):
                value = json.dumps(value, default=str)
            elif not isinstance(value, (str, bytes, int, float)):
                value = str(value)

            ttl_value = ttl or self.default_ttl
            success = await self.redis.setex(key, ttl_value, value)
            if success:
                self._sets += 1
            return bool(success)

        except Exception as e:
            logger.warning(f"Redis set failed: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from Redis cache."""
        try:
            await self._ensure_connection()
            if not self.redis:
                return False
            result = await self.redis.delete(key)
            if result:
                self._deletes += 1
            return bool(result)
        except Exception as e:
            logger.warning(f"Redis delete failed: {e}")
            return False

    async def clear(self) -> bool:
        """Clear all values from Redis cache."""
        try:
            await self._ensure_connection()
            if not self.redis:
                return False
            await self.redis.flushdb()
            return True
        except Exception as e:
            logger.warning(f"Redis clear failed: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis cache."""
        try:
            await self._ensure_connection()
            if not self.redis:
                return False
            return bool(await self.redis.exists(key))
        except Exception as e:
            logger.warning(f"Redis exists failed: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get Redis cache statistics."""
        return {
            "type": "redis",
            "url": self.url,
            "connected": self._connected,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": self._hits / max(self._hits + self._misses, 1),
            "sets": self._sets,
            "deletes": self._deletes
        }


class MultiLevelCache(CacheStrategy):
    """Multi-level caching with L1 (memory) and L2 (Redis) layers."""

    def __init__(self, l1_cache: Optional[CacheStrategy] = None, l2_cache: Optional[CacheStrategy] = None):
        self.l1_cache = l1_cache or MemoryCache()
        self.l2_cache = l2_cache
        self._read_through = False
        self._write_through = False

    def set_read_through(self, enabled: bool = True) -> None:
        """Enable/disable read-through caching."""
        self._read_through = enabled

    def set_write_through(self, enabled: bool = True) -> None:
        """Enable/disable write-through caching."""
        self._write_through = enabled

    async def get(self, key: str) -> Optional[Any]:
        """Get value using multi-level cache strategy."""
        # Try L1 cache first
        value = await self.l1_cache.get(key)
        if value is not None:
            # Background refresh of L2 if available
            if self.l2_cache:
                asyncio.create_task(self._background_l2_refresh(key, value))
            return value

        # Try L2 cache if available
        if self.l2_cache:
            value = await self.l2_cache.get(key)
            if value is not None:
                # Populate L1 cache
                await self.l1_cache.set(key, value)
                return value

        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in multi-level cache."""
        l1_success = await self.l1_cache.set(key, value, ttl)

        if self.l2_cache:
            l2_success = await self.l2_cache.set(key, value, ttl)

            if self._write_through:
                return l1_success and l2_success
            else:
                return l1_success  # L1 is primary for write-through
        else:
            return l1_success

    async def delete(self, key: str) -> bool:
        """Delete value from multi-level cache."""
        l1_success = await self.l1_cache.delete(key)
        l2_success = True

        if self.l2_cache:
            l2_success = await self.l2_cache.delete(key)

        return l1_success and l2_success

    async def clear(self) -> bool:
        """Clear all levels of cache."""
        l1_success = await self.l1_cache.clear()
        l2_success = True

        if self.l2_cache:
            l2_success = await self.l2_cache.clear()

        return l1_success and l2_success

    async def exists(self, key: str) -> bool:
        """Check if key exists in multi-level cache."""
        # Check L1 first
        if await self.l1_cache.exists(key):
            return True

        # Check L2 if available
        if self.l2_cache:
            return await self.l2_cache.exists(key)

        return False

    async def _background_l2_refresh(self, key: str, value: Any) -> None:
        """Background refresh of L2 cache."""
        if self.l2_cache:
            try:
                await self.l2_cache.set(key, value)
            except Exception as e:
                logger.warning(f"Background L2 refresh failed for key {key}: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get multi-level cache statistics."""
        stats = {
            "l1": self.l1_cache.get_stats(),
            "read_through": self._read_through,
            "write_through": self._write_through
        }

        if self.l2_cache:
            stats["l2"] = self.l2_cache.get_stats()

        return stats


class CacheManager:
    """Central cache management system."""

    def __init__(self) -> None:
        self.config_manager = get_global_config_manager()
        self.observability = get_global_observability_manager()
        self.error_handler = get_global_error_handler()

        # Cache instances
        self.framework_cache: Optional[CacheStrategy] = None
        self.protocol_cache: Optional[CacheStrategy] = None
        self.memory_cache: Optional[CacheStrategy] = None
        self.conversation_cache: Optional[CacheStrategy] = None

        self._initialized = False

    async def initialize(self) -> None:
        """Initialize cache manager."""
        if self._initialized:
            return

        try:
            # Get Redis configuration
            redis_url = await self.config_manager.get_value("redis_url")

            # Initialize caches based on configuration
            if redis_url:
                # Use multi-level caching with Redis L2
                redis_cache = RedisCache(str(redis_url))

                self.framework_cache = MultiLevelCache(MemoryCache(100), redis_cache)
                self.protocol_cache = MultiLevelCache(MemoryCache(50), redis_cache)
                self.memory_cache = MultiLevelCache(MemoryCache(200), redis_cache)
                self.conversation_cache = MultiLevelCache(MemoryCache(500), redis_cache)

                # Enable write-through for consistency
                for cache in [self.framework_cache, self.protocol_cache, self.memory_cache, self.conversation_cache]:
                    if isinstance(cache, MultiLevelCache):
                        cache.set_write_through(True)

            else:
                # Fallback to memory-only caching
                logger.warning("Redis not configured, using memory-only caching")
                self.framework_cache = MemoryCache(100)
                self.protocol_cache = MemoryCache(50)
                self.memory_cache = MemoryCache(200)
                self.conversation_cache = MemoryCache(500)

            logger.info("Cache manager initialized")

        except Exception as e:
            logger.error(f"Cache manager initialization failed: {e}")
            await self.error_handler.handle_error(e)

        self._initialized = True

    def get_cache(self, cache_type: str) -> Optional[CacheStrategy]:
        """Get cache instance by type."""
        caches = {
            "framework": self.framework_cache,
            "protocol": self.protocol_cache,
            "memory": self.memory_cache,
            "conversation": self.conversation_cache
        }
        return caches.get(cache_type)

    @asynccontextmanager
    async def cached_operation(self, cache_type: str, key: str, ttl: Optional[int] = None) -> AsyncGenerator[None, None]:
        """Context manager for cached operations."""
        cache = self.get_cache(cache_type)
        if not cache:
            # No caching available, just yield
            yield
            return

        # Try to get from cache first
        cached_result = await cache.get(key)
        if cached_result is not None:
            # Record cache hit
            await self.observability.record_business_event("cache_hit", {
                "cache_type": cache_type,
                "key": key
            })
            yield cached_result
            return

        # Cache miss - execute operation and cache result
        result_container = {"result": None}

        try:
            yield result_container

            # Cache the result
            if result_container["result"] is not None:
                await cache.set(key, result_container["result"], ttl)
                await self.observability.record_business_event("cache_miss_stored", {
                    "cache_type": cache_type,
                    "key": key
                })

        except Exception as e:
            # Don't cache errors
            await self.observability.record_business_event("cache_miss_error", {
                "cache_type": cache_type,
                "key": key,
                "error": str(e)
            })
            raise

    def cached(self, cache_type: str, key_template: Optional[str] = None, ttl: Optional[int] = None) -> Callable:
        """Decorator for caching function results."""
        def decorator(func: Callable) -> Callable:
            cache_key_template = key_template or f"{func.__module__}.{func.__name__}"
            cache_ttl = ttl

            @wraps(func)
            async def wrapper(*args: Any, **kwargs: Any) -> Any:
                # Generate cache key
                key_parts = [cache_key_template]
                if args:
                    key_parts.append(str(hash(str(args))))
                if kwargs:
                    key_parts.append(str(hash(str(sorted(kwargs.items())))))
                cache_key = ":".join(key_parts)

                cache = self.get_cache(cache_type)
                if cache:
                    # Try cache first
                    cached_result = await cache.get(cache_key)
                    if cached_result is not None:
                        await self.observability.record_business_event("cache_hit", {
                            "function": f"{func.__module__}.{func.__name__}",
                            "key": cache_key
                        })
                        return cached_result

                    # Execute function
                    start_time = time.time()
                    result = await func(*args, **kwargs)
                    execution_time = time.time() - start_time

                    # Cache result
                    await cache.set(cache_key, result, cache_ttl)

                    await self.observability.record_business_event("function_cached", {
                        "function": f"{func.__module__}.{func.__name__}",
                        "execution_time": execution_time,
                        "key": cache_key
                    })

                    return result
                else:
                    # No caching, just execute
                    return await func(*args, **kwargs)

            return wrapper
        return decorator

    async def invalidate_cache(self, cache_type: str, pattern: str = "*") -> int:
        """Invalidate cache entries matching pattern."""
        cache = self.get_cache(cache_type)
        if not cache:
            return 0

        # For now, clear entire cache (could implement pattern matching)
        success = await cache.clear()
        return 1 if success else 0

    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        stats = {}

        for cache_name in ["framework", "protocol", "memory", "conversation"]:
            cache = self.get_cache(cache_name)
            if cache:
                stats[cache_name] = cache.get_stats()

        return stats

    @property
    def cache(self) -> Optional[CacheStrategy]:
        """Get the default cache instance (memory cache)."""
        return self.memory_cache

    async def warmup_cache(self) -> None:
        """Warm up caches with commonly accessed data."""
        try:
            # Warm up framework cache
            if self.framework_cache:
                # Cache constitution and principles
                await self.cached("framework", "constitution")(lambda: None)()
                await self.cached("framework", "principles")(lambda: None)()

            logger.info("Cache warmup completed")

        except Exception as e:
            logger.warning(f"Cache warmup failed: {e}")

    async def health_check(self) -> Dict[str, Any]:
        """Perform cache health check."""
        health_results = {}

        for cache_name in ["framework", "protocol", "memory", "conversation"]:
            cache = self.get_cache(cache_name)
            if cache:
                try:
                    # Test basic operations
                    test_key = f"health_check_{int(time.time() * 1000)}"
                    await cache.set(test_key, "test_value", ttl=10)
                    retrieved = await cache.get(test_key)
                    await cache.delete(test_key)

                    health_results[cache_name] = {
                        "healthy": retrieved == "test_value",
                        **cache.get_stats()
                    }
                except Exception as e:
                    health_results[cache_name] = {
                        "healthy": False,
                        "error": str(e)
                    }
            else:
                health_results[cache_name] = {
                    "healthy": False,
                    "reason": "cache_not_initialized"
                }

        overall_healthy = all(result.get("healthy", False) for result in health_results.values())

        return {
            "healthy": overall_healthy,
            "caches": health_results,
            "timestamp": datetime.now().isoformat()
        }


# Global cache manager instance
_cache_manager: Optional[CacheManager] = None

def get_global_cache_manager() -> CacheManager:
    """Get the global cache manager instance."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager

def set_global_cache_manager(manager: CacheManager) -> None:
    """Set the global cache manager instance."""
    global _cache_manager
    _cache_manager = manager


# Cache-related decorators for common use cases
def cached_framework(ttl: int = 3600) -> Callable:
    """Decorator for framework-related caching."""
    def decorator(func: Callable) -> Callable:
        cache_manager = get_global_cache_manager()
        return cache_manager.cached("framework", ttl=ttl)(func)
    return decorator

def cached_protocol(ttl: int = 1800) -> Callable:
    """Decorator for protocol-related caching."""
    def decorator(func: Callable) -> Callable:
        cache_manager = get_global_cache_manager()
        return cache_manager.cached("protocol", ttl=ttl)(func)
    return decorator

def cached_memory(ttl: int = 7200) -> Callable:
    """Decorator for memory bank caching."""
    def decorator(func: Callable) -> Callable:
        cache_manager = get_global_cache_manager()
        return cache_manager.cached("memory", ttl=ttl)(func)
    return decorator

def cached_conversation(ttl: int = 3600) -> Callable:
    """Decorator for conversation caching."""
    def decorator(func: Callable) -> Callable:
        cache_manager = get_global_cache_manager()
        return cache_manager.cached("conversation", ttl=ttl)(func)
    return decorator
