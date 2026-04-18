"""
Language-Aware Query Cache Module

Provides multi-language query result caching with:
- Language + query hash based keys
- Per-language TTL (1 hour)
- Cache invalidation hooks
- Hit rate tracking
- Graceful fallback if Redis unavailable
"""

import hashlib
import json
import logging
import os
import pickle
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from enum import Enum

import redis
from redis.exceptions import ConnectionError, RedisError

logger = logging.getLogger(__name__)


class Language(str, Enum):
    """Supported languages for caching."""
    ENGLISH = "en"
    HINDI = "hi"


class CacheStats:
    """Track cache performance metrics."""
    
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.errors = 0
        self.last_invalidation = None
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate (0.0 - 1.0)."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Export as dictionary."""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": self.hit_rate,
            "evictions": self.evictions,
            "errors": self.errors,
            "last_invalidation": self.last_invalidation.isoformat() if self.last_invalidation else None
        }
    
    def reset(self):
        """Reset all counters."""
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.errors = 0


class LanguageAwareCacheKey:
    """Generate cache keys with language awareness."""
    
    @staticmethod
    def generate_key(
        query: str,
        language: Language,
        with_filters: bool = False
    ) -> str:
        """
        Generate cache key for query + language.
        
        Format: cache:query:{language}:{query_hash}:{filter_flag}
        
        Args:
            query: User query text
            language: Target language (en/hi)
            with_filters: Whether filters were applied
        
        Returns:
            Cache key string
        """
        # Normalize query (lowercase, strip whitespace)
        normalized = query.lower().strip()
        
        # Create MD5 hash of query
        query_hash = hashlib.md5(normalized.encode()).hexdigest()[:12]
        
        # Build key with language prefix
        filter_suffix = ":filtered" if with_filters else ":unfiltered"
        
        return f"cache:query:{language.value}:{query_hash}{filter_suffix}"
    
    @staticmethod
    def generate_language_key(language: Language) -> str:
        """Generate pattern for all queries in a language."""
        return f"cache:query:{language.value}:*"
    
    @staticmethod
    def generate_all_cache_pattern() -> str:
        """Generate pattern for ALL cache entries."""
        return "cache:query:*"


class LanguageAwareCache:
    """
    Multi-language query result cache with Redis backend.
    
    Features:
    - Language-specific caching
    - Per-language TTL (1 hour default)
    - Graceful fallback if Redis unavailable
    - Cache invalidation hooks
    - Hit rate tracking
    """
    
    def __init__(
        self,
        redis_url: Optional[str] = None,
        default_ttl_seconds: int = 3600,  # 1 hour
        enable_fallback: bool = True
    ):
        """
        Initialize cache.
        
        Args:
            redis_url: Redis connection URL (default: env REDIS_URL)
            default_ttl_seconds: Default TTL per language (1 hour)
            enable_fallback: Enable in-memory fallback if Redis unavailable
        """
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.default_ttl = default_ttl_seconds
        self.enable_fallback = enable_fallback
        
        # Try to connect to Redis
        self.redis_client = self._connect_redis()
        self.available = self.redis_client is not None
        
        # In-memory fallback cache
        self._fallback_cache: Dict[str, Dict[str, Any]] = {}
        
        # Statistics
        self.stats = CacheStats()
        
        logger.info(
            f"LanguageAwareCache initialized "
            f"(Redis: {'connected' if self.available else 'unavailable'}, "
            f"Fallback: {'enabled' if self.enable_fallback else 'disabled'})"
        )
    
    def _connect_redis(self) -> Optional[redis.Redis]:
        """Attempt to connect to Redis."""
        try:
            client = redis.Redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True
            )
            # Test connection
            client.ping()
            logger.info("Connected to Redis successfully")
            return client
        except (ConnectionError, RedisError) as e:
            logger.warning(f"Failed to connect to Redis: {e}")
            if self.enable_fallback:
                logger.info("Fallback in-memory cache enabled")
            return None
    
    def get(
        self,
        query: str,
        language: Language
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached response for query in specified language.
        
        Args:
            query: User query
            language: Target language
        
        Returns:
            Cached response dict or None if not found
        """
        key = LanguageAwareCacheKey.generate_key(query, language)
        
        try:
            if self.available and self.redis_client:
                # Try Redis first
                cached_value = self.redis_client.get(key)
                if cached_value:
                    self.stats.hits += 1
                    try:
                        return json.loads(cached_value)
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to decode cached value for key: {key}")
                        self.stats.errors += 1
                        return None
            else:
                # Use fallback cache
                if key in self._fallback_cache:
                    entry = self._fallback_cache[key]
                    # Check expiration
                    if entry["expires_at"] > datetime.now():
                        self.stats.hits += 1
                        return entry["value"]
                    else:
                        # Expired, remove it
                        del self._fallback_cache[key]
                        self.stats.evictions += 1
            
            self.stats.misses += 1
            return None
        
        except Exception as e:
            logger.error(f"Error retrieving from cache: {e}")
            self.stats.errors += 1
            return None
    
    def set(
        self,
        query: str,
        language: Language,
        response: Dict[str, Any],
        ttl_seconds: Optional[int] = None
    ) -> bool:
        """
        Cache response for query in specified language.
        
        Args:
            query: User query
            language: Target language
            response: Response to cache
            ttl_seconds: Custom TTL (default: 1 hour)
        
        Returns:
            True if cached successfully, False otherwise
        """
        key = LanguageAwareCacheKey.generate_key(query, language)
        ttl = ttl_seconds or self.default_ttl
        
        try:
            if self.available and self.redis_client:
                # Cache to Redis
                self.redis_client.setex(
                    key,
                    ttl,
                    json.dumps(response)
                )
                return True
            else:
                # Cache to fallback
                self._fallback_cache[key] = {
                    "value": response,
                    "expires_at": datetime.now() + timedelta(seconds=ttl),
                    "created_at": datetime.now()
                }
                return True
        
        except Exception as e:
            logger.error(f"Error setting cache: {e}")
            self.stats.errors += 1
            return False
    
    def delete(self, query: str, language: Language) -> bool:
        """
        Delete cache entry for specific query + language.
        
        Args:
            query: User query
            language: Target language
        
        Returns:
            True if deleted, False if not found
        """
        key = LanguageAwareCacheKey.generate_key(query, language)
        
        try:
            if self.available and self.redis_client:
                result = self.redis_client.delete(key)
                return result > 0
            else:
                if key in self._fallback_cache:
                    del self._fallback_cache[key]
                    return True
            return False
        
        except Exception as e:
            logger.error(f"Error deleting cache entry: {e}")
            self.stats.errors += 1
            return False
    
    def invalidate_language(self, language: Language) -> int:
        """
        Invalidate all cache entries for a specific language.
        
        Args:
            language: Language to invalidate
        
        Returns:
            Number of entries deleted
        """
        pattern = LanguageAwareCacheKey.generate_language_key(language)
        count = 0
        
        try:
            if self.available and self.redis_client:
                # Use SCAN to avoid blocking on large datasets
                cursor = 0
                while True:
                    cursor, keys = self.redis_client.scan(
                        cursor,
                        match=pattern,
                        count=100
                    )
                    if keys:
                        count += self.redis_client.delete(*keys)
                    if cursor == 0:
                        break
            else:
                # Fallback: filter and delete
                keys_to_delete = [
                    k for k in self._fallback_cache.keys()
                    if f":{language.value}:" in k
                ]
                for key in keys_to_delete:
                    del self._fallback_cache[key]
                count = len(keys_to_delete)
        
        except Exception as e:
            logger.error(f"Error invalidating language cache: {e}")
            self.stats.errors += 1
        
        if count > 0:
            self.stats.evictions += count
            self.stats.last_invalidation = datetime.now()
            logger.info(f"Invalidated {count} cache entries for language: {language.value}")
        
        return count
    
    def invalidate_all(self) -> int:
        """
        Invalidate all cache entries (full cache clear).
        
        Used after daily scraper completes or for emergency purge.
        
        Returns:
            Number of entries deleted
        """
        pattern = LanguageAwareCacheKey.generate_all_cache_pattern()
        count = 0
        
        try:
            if self.available and self.redis_client:
                cursor = 0
                while True:
                    cursor, keys = self.redis_client.scan(
                        cursor,
                        match=pattern,
                        count=100
                    )
                    if keys:
                        count += self.redis_client.delete(*keys)
                    if cursor == 0:
                        break
            else:
                # Fallback: clear all
                count = len(self._fallback_cache)
                self._fallback_cache.clear()
        
        except Exception as e:
            logger.error(f"Error clearing all cache: {e}")
            self.stats.errors += 1
        
        if count > 0:
            self.stats.evictions += count
            self.stats.last_invalidation = datetime.now()
            logger.info(f"Cleared {count} cache entries (full purge)")
        
        return count
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        return {
            **self.stats.to_dict(),
            "redis_available": self.available,
            "fallback_cache_size": len(self._fallback_cache),
            "ttl_seconds": self.default_ttl
        }
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check cache health status.
        
        Returns:
            Health status dict
        """
        status = {
            "healthy": True,
            "redis_connected": self.available,
            "fallback_active": len(self._fallback_cache) > 0,
            "cache_stats": self.get_stats(),
            "timestamp": datetime.now().isoformat()
        }
        
        # Check Redis connectivity if supposedly available
        if self.available and self.redis_client:
            try:
                self.redis_client.ping()
                status["redis_status"] = "connected"
            except Exception as e:
                status["redis_status"] = f"error: {str(e)}"
                status["healthy"] = False
        else:
            status["redis_status"] = "disconnected"
        
        return status


# Global cache instance
_cache_instance: Optional[LanguageAwareCache] = None


def get_cache() -> LanguageAwareCache:
    """Get or create global cache instance."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = LanguageAwareCache()
    return _cache_instance


def create_cache(
    redis_url: Optional[str] = None,
    default_ttl_seconds: int = 3600,
    enable_fallback: bool = True
) -> LanguageAwareCache:
    """
    Create new cache instance.
    
    Args:
        redis_url: Redis URL
        default_ttl_seconds: Default TTL
        enable_fallback: Enable fallback cache
    
    Returns:
        LanguageAwareCache instance
    """
    return LanguageAwareCache(
        redis_url=redis_url,
        default_ttl_seconds=default_ttl_seconds,
        enable_fallback=enable_fallback
    )


# Utility functions for API integration
def cache_query_result(
    query: str,
    language: Language,
    response: Dict[str, Any],
    ttl_seconds: int = 3600
) -> bool:
    """Cache query result."""
    cache = get_cache()
    return cache.set(query, language, response, ttl_seconds)


def get_cached_result(
    query: str,
    language: Language
) -> Optional[Dict[str, Any]]:
    """Get cached query result."""
    cache = get_cache()
    return cache.get(query, language)


def clear_language_cache(language: Language) -> int:
    """Clear cache for specific language."""
    cache = get_cache()
    return cache.invalidate_language(language)


def clear_all_cache() -> int:
    """Clear all cache entries."""
    cache = get_cache()
    return cache.invalidate_all()
