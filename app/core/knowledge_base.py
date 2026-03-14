"""Knowledge base module for document storage and retrieval"""
from typing import List, Optional, Tuple
import numpy as np

from app.config import settings
from app.core.embedding import embedding_generator
from app.db.faiss_manager import faiss_manager


class KnowledgeBase:
    """Knowledge base for document storage and semantic search"""
    
    def __init__(self):
        self.embedding_gen = embedding_generator
        self.faiss_mgr = faiss_manager
    
    async def add_document_chunks(
        self,
        intent_space: str,
        document_id: str,
        chunks: List[dict]
    ) -> bool:
        """
        Add document chunks to knowledge base
        
        Args:
            intent_space: Target intent space (e.g., "HR", "Legal")
            document_id: Document ID
            chunks: List of chunk dictionaries with 'text' key
        
        Returns:
            bool: Success status
        """
        if not chunks:
            return True
        
        # Extract texts from chunks
        texts = [chunk["text"] for chunk in chunks]
        
        # Generate embeddings
        embeddings = self.embedding_gen.generate(texts)
        
        if len(embeddings) == 0:
            return False
        
        # Add to FAISS
        success = self.faiss_mgr.add_chunks(intent_space, embeddings, chunks)
        
        return success
    
    async def search(
        self,
        query: str,
        intent_space: str,
        top_k: int = 5
    ) -> List[Tuple[dict, float]]:
        """
        Search knowledge base for relevant chunks
        
        Args:
            query: Search query
            intent_space: Intent space to search
            top_k: Number of results to return
        
        Returns:
            List of (metadata, distance) tuples
        """
        # Generate query embedding
        query_embedding = self.embedding_gen.generate_single(query)
        
        # Search FAISS
        results = self.faiss_mgr.search(
            intent_space=intent_space,
            query_embedding=query_embedding,
            top_k=top_k
        )
        
        return results
    
    async def search_multi_space(
        self,
        query: str,
        intent_spaces: List[str],
        top_k_per_space: int = 3
    ) -> List[Tuple[dict, float]]:
        """
        Search across multiple intent spaces
        
        Args:
            query: Search query
            intent_spaces: List of intent spaces to search
            top_k_per_space: Number of results per space
        
        Returns:
            Combined and sorted list of results
        """
        all_results = []
        
        query_embedding = self.embedding_gen.generate_single(query)
        
        for space in intent_spaces:
            results = self.faiss_mgr.search(
                intent_space=space,
                query_embedding=query_embedding,
                top_k=top_k_per_space
            )
            all_results.extend(results)
        
        # Sort by score (lower distance = higher score)
        all_results.sort(key=lambda x: x[1])
        
        return all_results
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a list of texts."""
        if not texts:
            return np.array([])
        return self.embedding_gen.generate(texts)
    
    def generate_single_embedding(self, text: str) -> np.ndarray:
        return self.embedding_gen.generate_single(text)
    
    def get_stats(self, intent_space: Optional[str] = None) -> dict:
        return self.faiss_mgr.get_stats(intent_space)


# Global knowledge base instance
knowledge_base = KnowledgeBase()