"""Embedding module for generating text embeddings"""
import hashlib
import time
from typing import List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer

from app.config import settings


class EmbeddingCache:
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache = {}
        self.access_order = []
    
    def _get_key(self, text: str) -> str:
        return hashlib.md5(text.encode()).hexdigest()
    
    def get(self, text: str) -> Optional[np.ndarray]:
        key = self._get_key(text)
        if key in self.cache:
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None
    
    def set(self, text: str, embedding: np.ndarray):
        key = self._get_key(text)
        if key in self.cache:
            self.access_order.remove(key)
        elif len(self.cache) >= self.max_size:
            oldest = self.access_order.pop(0)
            del self.cache[oldest]
        
        self.cache[key] = embedding
        self.access_order.append(key)


class EmbeddingGenerator:
    def __init__(self):
        self.model_name = settings.EMBEDDING_MODEL
        self._model = None
        self.cache = EmbeddingCache(max_size=1000)
        self._download_model()
    
    def _download_model(self):
        try:
            print(f"Loading embedding model: {self.model_name}")
            start = time.time()
            _ = self.model
            elapsed = time.time() - start
            print(f"Embedding model ready in {elapsed:.1f}s")
        except Exception as e:
            print(f"Warning: Could not load embedding model: {e}")
    
    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            self._model = SentenceTransformer(self.model_name)
        return self._model
    
    def generate(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of texts
        
        Args:
            texts: List of text strings
        
        Returns:
            numpy array of embeddings (shape: len(texts) x 384)
        """
        if not texts:
            return np.array([])
        
        # Filter out empty texts
        valid_texts = [t for t in texts if t and len(t.strip()) > 0]
        if not valid_texts:
            return np.array([])
        
        # Generate embeddings
        embeddings = self.model.encode(
            valid_texts,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        
        return embeddings.astype(np.float32)
    
    def generate_single(self, text: str) -> np.ndarray:
        if not text or not text.strip():
            return np.zeros(384, dtype=np.float32)
        
        # Check cache first
        cached = self.cache.get(text)
        if cached is not None:
            return cached
        
        # Generate and cache
        embedding = self.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        result = embedding.astype(np.float32)
        self.cache.set(text, result)
        return result
    
    @property
    def dimension(self) -> int:
        """Return embedding dimension"""
        return 384


# Global embedding generator instance
embedding_generator = EmbeddingGenerator()