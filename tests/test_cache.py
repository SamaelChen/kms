"""Unit tests for cache module"""
import pytest
import time
from datetime import datetime, timedelta

from app.core.cache import QueryCache


class TestQueryCache:
    def test_cache_initialization(self):
        cache = QueryCache()
        assert cache.cache == {}
        assert cache.ttl_seconds == 300  # 5 minutes default
    
    def test_cache_with_custom_ttl(self):
        cache = QueryCache(ttl_seconds=600)
        assert cache.ttl_seconds == 600
    
    def test_cache_get_miss(self):
        cache = QueryCache()
        result = cache.get("unknown query", "General")
        assert result is None
    
    def test_cache_set_and_get(self):
        cache = QueryCache()
        data = {"response": "test", "confidence": 0.9}
        
        cache.set("test query", "HR", data)
        result = cache.get("test query", "HR")
        
        assert result == data
    
    def test_cache_key_isolation(self):
        cache = QueryCache()
        data_hr = {"response": "HR answer"}
        data_legal = {"response": "Legal answer"}
        
        cache.set("policy question", "HR", data_hr)
        cache.set("policy question", "Legal", data_legal)
        
        assert cache.get("policy question", "HR") == data_hr
        assert cache.get("policy question", "Legal") == data_legal
    
    def test_cache_ttl_expiration(self):
        cache = QueryCache(ttl_seconds=0)  # Immediate expiration
        data = {"response": "test"}
        
        cache.set("query", "General", data)
        time.sleep(0.1)  # Small delay
        result = cache.get("query", "General")
        
        assert result is None  # Expired
    
    def test_cache_delete(self):
        cache = QueryCache()
        data = {"response": "test"}
        
        cache.set("query", "General", data)
        cache.delete("query", "General")
        
        assert cache.get("query", "General") is None
    
    def test_cache_clear(self):
        cache = QueryCache()
        
        cache.set("q1", "HR", {"r": "1"})
        cache.set("q2", "Legal", {"r": "2"})
        cache.clear()
        
        assert cache.get("q1", "HR") is None
        assert cache.get("q2", "Legal") is None
    
    def test_cache_size(self):
        cache = QueryCache()
        
        cache.set("q1", "HR", {"r": "1"})
        cache.set("q2", "Legal", {"r": "2"})
        
        assert cache.size() == 2
    
    def test_get_stats(self):
        cache = QueryCache()
        
        cache.set("q1", "HR", {"r": "1"})
        cache.set("q2", "Legal", {"r": "2"})
        cache.get("q1", "HR")  # Hit
        cache.get("q3", "Finance")  # Miss
        
        stats = cache.get_stats()
        assert stats["total_entries"] == 2
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert "hit_rate" in stats
    
    def test_multiple_same_query_different_spaces(self):
        cache = QueryCache()
        
        cache.set("leave policy", "HR", {"response": "20 days"})
        cache.set("leave policy", "Legal", {"response": "As per contract"})
        
        hr_result = cache.get("leave policy", "HR")
        legal_result = cache.get("leave policy", "Legal")
        
        assert hr_result["response"] == "20 days"
        assert legal_result["response"] == "As per contract"
