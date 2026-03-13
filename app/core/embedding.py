"""Embedding module for generating text embeddings"""
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer

from app.config import settings


class EmbeddingGenerator:
    """Generate embeddings using sentence-transformers"""
    
    def __init__(self):
        self.model_name = settings.EMBEDDING_MODEL
        self._model = None
    
    @property
    def model(self) -> SentenceTransformer:
        """Lazy load the model"""
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
        """
        Generate embedding for a single text
        
        Args:
            text: Input text
        
        Returns:
            numpy array of shape (384,)
        """
        if not text or not text.strip():
            # Return zero vector for empty text
            return np.zeros(384, dtype=np.float32)
        
        embedding = self.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        
        return embedding.astype(np.float32)
    
    @property
    def dimension(self) -> int:
        """Return embedding dimension"""
        return 384


# Global embedding generator instance
embedding_generator = EmbeddingGenerator()