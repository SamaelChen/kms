"""Caching utilities for query results"""
import time
from typing import Optional, Any, Dict, Tuple


class QueryCache:
    def __init__(self, ttl: int = 300):
        self.ttl = ttl
        self.cache: Dict[str, Tuple[Any, float]] = {}
    
    def _get_key(self, query: str, intent_space: str) -> str:
        return f"{intent_space}:{hash(query) % 10000000}"
    
    def get(self, query: str, intent_space: str) -> Optional[Any]:
        key = self._get_key(query, intent_space)
        if key in self.cache:
            result, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return result
            del self.cache[key]
        return None
    
    def set(self, query: str, intent_space: str, result: Any):
        key = self._get_key(query, intent_space)
        self.cache[key] = (result, time.time())
    
    def clear(self):
        self.cache.clear()
    
    def get_stats(self) -> dict:
        return {
            "entries": len(self.cache),
            "ttl_seconds": self.ttl
        }


# Global query cache instance
query_cache = QueryCache()
