"""TTL cache implementation"""

import time
from typing import Any, Dict, Optional
from threading import Lock
import asyncio
from functools import wraps


class TTLCache:
    """Thread-safe TTL cache implementation"""
    
    def __init__(self, ttl_seconds: int = 3600, max_size: int = 1000):
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self._cache: Dict[str, tuple[Any, float]] = {}
        self._lock = Lock()
        self._access_times: Dict[str, float] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        with self._lock:
            if key in self._cache:
                value, expiry = self._cache[key]
                if time.time() < expiry:
                    self._access_times[key] = time.time()
                    return value
                else:
                    # Remove expired entry
                    del self._cache[key]
                    if key in self._access_times:
                        del self._access_times[key]
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL"""
        ttl = ttl or self.ttl_seconds
        expiry = time.time() + ttl
        
        with self._lock:
            # Check size limit
            if len(self._cache) >= self.max_size and key not in self._cache:
                # Remove least recently used
                self._evict_lru()
            
            self._cache[key] = (value, expiry)
            self._access_times[key] = time.time()
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                if key in self._access_times:
                    del self._access_times[key]
                return True
        return False
    
    def clear(self) -> None:
        """Clear all cache entries"""
        with self._lock:
            self._cache.clear()
            self._access_times.clear()
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry"""
        if not self._access_times:
            return
        
        lru_key = min(self._access_times, key=self._access_times.get)
        del self._cache[lru_key]
        del self._access_times[lru_key]
    
    def cleanup_expired(self) -> int:
        """Remove all expired entries"""
        current_time = time.time()
        expired_keys = []
        
        with self._lock:
            for key, (_, expiry) in self._cache.items():
                if current_time >= expiry:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._cache[key]
                if key in self._access_times:
                    del self._access_times[key]
        
        return len(expired_keys)


def cached(ttl_seconds: int = 300):
    """Decorator for caching function results"""
    def decorator(func):
        cache = TTLCache(ttl_seconds=ttl_seconds)
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Check cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Call function and cache result
            result = await func(*args, **kwargs)
            cache.set(cache_key, result)
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Check cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result)
            return result
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator