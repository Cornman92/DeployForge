"""Tests for caching layer."""

import pytest
import time
from deployforge.cache import Cache, CacheEntry


def test_cache_entry_not_expired():
    """Test cache entry expiration check."""
    entry = CacheEntry(
        key="test",
        value="data",
        timestamp=time.time(),
        ttl=3600
    )
    assert not entry.is_expired()


def test_cache_entry_expired():
    """Test expired cache entry."""
    entry = CacheEntry(
        key="test",
        value="data",
        timestamp=time.time() - 7200,  # 2 hours ago
        ttl=3600  # 1 hour TTL
    )
    assert entry.is_expired()


def test_cache_entry_no_ttl():
    """Test cache entry with no TTL never expires."""
    entry = CacheEntry(
        key="test",
        value="data",
        timestamp=time.time() - 86400,  # 1 day ago
        ttl=None
    )
    assert not entry.is_expired()


def test_cache_set_and_get(cache_dir):
    """Test setting and getting cache values."""
    cache = Cache(cache_dir)

    cache.set("test_key", {"data": "value"})
    result = cache.get("test_key")

    assert result == {"data": "value"}


def test_cache_get_nonexistent(cache_dir):
    """Test getting non-existent key."""
    cache = Cache(cache_dir)

    result = cache.get("nonexistent", default="default_value")
    assert result == "default_value"


def test_cache_delete(cache_dir):
    """Test deleting cache entry."""
    cache = Cache(cache_dir)

    cache.set("test_key", "value")
    assert cache.get("test_key") == "value"

    cache.delete("test_key")
    assert cache.get("test_key") is None


def test_cache_clear(cache_dir):
    """Test clearing all cache entries."""
    cache = Cache(cache_dir)

    cache.set("key1", "value1")
    cache.set("key2", "value2")

    cache.clear()

    assert cache.get("key1") is None
    assert cache.get("key2") is None


def test_cache_cleanup_expired(cache_dir):
    """Test cleaning up expired entries."""
    cache = Cache(cache_dir)

    # Add entries with different TTLs
    cache.set("fresh", "value1", ttl=3600)
    cache.set("expired", "value2", ttl=0)  # Immediately expired

    time.sleep(0.1)  # Wait a bit

    removed = cache.cleanup_expired()
    assert removed >= 1  # At least the expired one

    assert cache.get("fresh") is not None
