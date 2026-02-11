"""
Advanced caching system for improved performance
"""

import streamlit as st
import pandas as pd
import hashlib
import pickle
import time
from typing import Any, Optional, Callable
from functools import wraps
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    """
    Advanced caching system for Streamlit applications
    """
    
    def __init__(self, max_cache_size: int = 100):
        self.max_cache_size = max_cache_size
        self.cache = {}
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0
        }
    
    def _generate_cache_key(self, func_name: str, *args, **kwargs) -> str:
        """Generate a unique cache key for function arguments"""
        # Create a hash of the function name and arguments
        key_data = f"{func_name}:{str(args)}:{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _is_cache_valid(self, cache_entry: dict, max_age_seconds: int = 3600) -> bool:
        """Check if cache entry is still valid"""
        if max_age_seconds <= 0:
            return True
        
        age = time.time() - cache_entry['timestamp']
        return age < max_age_seconds
    
    def _evict_oldest(self):
        """Evict the oldest cache entry"""
        if not self.cache:
            return
        
        oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]['timestamp'])
        del self.cache[oldest_key]
        self.cache_stats['evictions'] += 1
        logger.info(f"Evicted cache entry: {oldest_key}")
    
    def get(self, key: str, max_age_seconds: int = 3600) -> Optional[Any]:
        """Get value from cache"""
        if key not in self.cache:
            self.cache_stats['misses'] += 1
            return None
        
        cache_entry = self.cache[key]
        
        if not self._is_cache_valid(cache_entry, max_age_seconds):
            del self.cache[key]
            self.cache_stats['misses'] += 1
            return None
        
        self.cache_stats['hits'] += 1
        return cache_entry['value']
    
    def set(self, key: str, value: Any, max_age_seconds: int = 3600):
        """Set value in cache"""
        # Evict oldest if cache is full
        if len(self.cache) >= self.max_cache_size:
            self._evict_oldest()
        
        self.cache[key] = {
            'value': value,
            'timestamp': time.time(),
            'max_age': max_age_seconds
        }
    
    def clear(self):
        """Clear all cache entries"""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = (self.cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'size': len(self.cache),
            'hits': self.cache_stats['hits'],
            'misses': self.cache_stats['misses'],
            'evictions': self.cache_stats['evictions'],
            'hit_rate': hit_rate
        }
    
    def cached_dataframe_operation(self, max_age_seconds: int = 1800):
        """
        Decorator for caching DataFrame operations
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = self._generate_cache_key(func.__name__, *args, **kwargs)
                
                # Try to get from cache
                cached_result = self.get(cache_key, max_age_seconds)
                if cached_result is not None:
                    logger.debug(f"Cache hit for {func.__name__}")
                    return cached_result
                
                # Execute function and cache result
                logger.debug(f"Cache miss for {func.__name__}, executing...")
                result = func(*args, **kwargs)
                
                # Only cache if result is a DataFrame or small object
                if isinstance(result, pd.DataFrame) and len(result) < 10000:
                    self.set(cache_key, result, max_age_seconds)
                elif not isinstance(result, pd.DataFrame) and len(str(result)) < 10000:
                    self.set(cache_key, result, max_age_seconds)
                
                return result
            
            return wrapper
        return decorator

# Global cache manager instance
cache_manager = CacheManager()

def streamlit_cache_dataframe(max_age_seconds: int = 1800):
    """
    Streamlit-compatible DataFrame caching decorator
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache_manager._generate_cache_key(func.__name__, *args, **kwargs)
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_key, max_age_seconds)
            if cached_result is not None:
                return cached_result
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Cache result if appropriate
            if isinstance(result, pd.DataFrame) and len(result) < 10000:
                cache_manager.set(cache_key, result, max_age_seconds)
            elif not isinstance(result, pd.DataFrame) and len(str(result)) < 10000:
                cache_manager.set(cache_key, result, max_age_seconds)
            
            return result
        
        return wrapper
    return decorator

def clear_all_caches():
    """Clear all caches"""
    cache_manager.clear()
    if hasattr(st, 'cache_data'):
        st.cache_data.clear()
    if hasattr(st, 'cache_resource'):
        st.cache_resource.clear()
    logger.info("All caches cleared")
