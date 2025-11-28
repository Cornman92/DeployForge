"""Caching layer for repeated operations."""

import hashlib
import json
import logging
import pickle
import time
from pathlib import Path
from typing import Any, Optional, Callable
from dataclasses import dataclass, asdict
from functools import wraps

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Represents a cache entry."""

    key: str
    value: Any
    timestamp: float
    ttl: Optional[int] = None  # Time to live in seconds
    metadata: dict = None

    def is_expired(self) -> bool:
        """Check if the cache entry has expired."""
        if self.ttl is None:
            return False
        return time.time() - self.timestamp > self.ttl


class Cache:
    """Simple file-based cache for repeated operations."""

    def __init__(self, cache_dir: Path, default_ttl: int = 3600):
        """
        Initialize cache.

        Args:
            cache_dir: Directory to store cache files
            default_ttl: Default time-to-live in seconds
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.default_ttl = default_ttl

    def _get_cache_path(self, key: str) -> Path:
        """Get the file path for a cache key."""
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.cache"

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from cache.

        Args:
            key: Cache key
            default: Default value if not found

        Returns:
            Cached value or default
        """
        cache_path = self._get_cache_path(key)

        if not cache_path.exists():
            return default

        try:
            with open(cache_path, "rb") as f:
                entry = pickle.load(f)

            if entry.is_expired():
                logger.debug(f"Cache entry expired: {key}")
                cache_path.unlink()
                return default

            logger.debug(f"Cache hit: {key}")
            return entry.value

        except Exception as e:
            logger.error(f"Error reading cache: {e}")
            return default

    def set(self, key: str, value: Any, ttl: Optional[int] = None, metadata: dict = None) -> None:
        """
        Set a value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            metadata: Optional metadata
        """
        if ttl is None:
            ttl = self.default_ttl

        entry = CacheEntry(
            key=key, value=value, timestamp=time.time(), ttl=ttl, metadata=metadata or {}
        )

        cache_path = self._get_cache_path(key)

        try:
            with open(cache_path, "wb") as f:
                pickle.dump(entry, f)

            logger.debug(f"Cache set: {key}")

        except Exception as e:
            logger.error(f"Error writing cache: {e}")

    def delete(self, key: str) -> None:
        """Delete a cache entry."""
        cache_path = self._get_cache_path(key)

        if cache_path.exists():
            cache_path.unlink()
            logger.debug(f"Cache deleted: {key}")

    def clear(self) -> None:
        """Clear all cache entries."""
        for cache_file in self.cache_dir.glob("*.cache"):
            cache_file.unlink()

        logger.info("Cache cleared")

    def cleanup_expired(self) -> int:
        """
        Remove expired cache entries.

        Returns:
            Number of entries removed
        """
        removed = 0

        for cache_file in self.cache_dir.glob("*.cache"):
            try:
                with open(cache_file, "rb") as f:
                    entry = pickle.load(f)

                if entry.is_expired():
                    cache_file.unlink()
                    removed += 1

            except Exception as e:
                logger.error(f"Error cleaning cache file {cache_file}: {e}")

        logger.info(f"Removed {removed} expired cache entries")
        return removed


def cached(cache_instance: Cache, ttl: Optional[int] = None, key_func: Optional[Callable] = None):
    """
    Decorator to cache function results.

    Args:
        cache_instance: Cache instance to use
        ttl: Time to live in seconds
        key_func: Optional function to generate cache key from args

    Returns:
        Decorated function
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"

            # Try to get from cache
            result = cache_instance.get(cache_key)

            if result is not None:
                return result

            # Execute function
            result = func(*args, **kwargs)

            # Store in cache
            cache_instance.set(cache_key, result, ttl=ttl)

            return result

        return wrapper

    return decorator
