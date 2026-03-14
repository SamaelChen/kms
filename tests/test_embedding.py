"""Unit tests for embedding module"""
import pytest
import numpy as np
from unittest.mock import Mock, patch

from app.core.embedding import EmbeddingCache, EmbeddingGenerator


class TestEmbeddingCache:
    def test_cache_initialization(self):
        cache = EmbeddingCache(max_size=100)
        assert cache.max_size == 100
        assert cache.cache == {}
        assert cache.access_order == []
    
    def test_cache_get_miss(self):
        cache = EmbeddingCache()
        result = cache.get("nonexistent text")
        assert result is None
    
    def test_cache_get_hit(self):
        cache = EmbeddingCache()
        embedding = np.array([1.0, 2.0, 3.0])
        cache.set("test text", embedding)
        
        result = cache.get("test text")
        assert np.array_equal(result, embedding)
    
    def test_cache_lru_eviction(self):
        cache = EmbeddingCache(max_size=2)
        emb1 = np.array([1.0])
        emb2 = np.array([2.0])
        emb3 = np.array([3.0])
        
        cache.set("text1", emb1)
        cache.set("text2", emb2)
        cache.get("text1")  # Access text1 to make it recently used
        cache.set("text3", emb3)  # Should evict text2
        
        assert cache.get("text1") is not None
        assert cache.get("text2") is None  # Evicted
        assert cache.get("text3") is not None
    
    def test_cache_update_existing(self):
        cache = EmbeddingCache()
        emb1 = np.array([1.0])
        emb2 = np.array([2.0])
        
        cache.set("text", emb1)
        cache.set("text", emb2)
        
        result = cache.get("text")
        assert np.array_equal(result, emb2)


class TestEmbeddingGenerator:
    @pytest.fixture
    def generator(self):
        return EmbeddingGenerator()
    
    def test_generator_initialization(self, generator):
        assert generator.model_name == "sentence-transformers/all-MiniLM-L6-v2"
        assert generator.cache is not None
    
    def test_generate_empty_list(self, generator):
        result = generator.generate([])
        assert len(result) == 0
    
    def test_generate_empty_strings(self, generator):
        result = generator.generate(["", "  ", None])
        assert len(result) == 0
    
    def test_generate_single_empty(self, generator):
        result = generator.generate_single("")
        assert result.shape == (384,)
        assert np.all(result == 0)
    
    def test_generate_single_whitespace(self, generator):
        result = generator.generate_single("   ")
        assert result.shape == (384,)
        assert np.all(result == 0)
    
    @patch('app.core.embedding.SentenceTransformer')
    def test_generate_with_mock(self, mock_transformer, generator):
        mock_model = Mock()
        mock_model.encode.return_value = np.array([[1.0] * 384])
        mock_transformer.return_value = mock_model
        
        generator._model = mock_model
        result = generator.generate(["test text"])
        
        assert result.shape == (1, 384)
        mock_model.encode.assert_called_once()
    
    @patch('app.core.embedding.SentenceTransformer')
    def test_generate_single_with_mock(self, mock_transformer, generator):
        mock_model = Mock()
        mock_model.encode.return_value = np.array([1.0] * 384)
        mock_transformer.return_value = mock_model
        
        generator._model = mock_model
        result = generator.generate_single("test text")
        
        assert result.shape == (384,)
        assert np.all(result == 1.0)
    
    def test_cache_is_used(self, generator):
        text = "cached text"
        embedding = np.array([1.0] * 384)
        
        generator.cache.set(text, embedding)
        result = generator.generate_single(text)
        
        assert np.array_equal(result, embedding)
