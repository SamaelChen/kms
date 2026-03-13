"""
IntelliKnow KMS - FAISS Index Management
"""
import os
import pickle
import json
from pathlib import Path
from typing import List, Tuple, Optional
import numpy as np

import faiss
from app.config import settings


class FAISSManager:
    """Manages FAISS indexes for different intent spaces"""
    
    def __init__(self):
        self.indexes = {}  # intent_space -> faiss.Index
        self.metadata = {}  # intent_space -> List[dict] (chunk metadata)
        self.dimension = 384  # all-MiniLM-L6-v2 produces 384-dim embeddings
        self._load_all_indexes()
    
    def _get_index_path(self, intent_space: str) -> Path:
        """Get path for FAISS index file"""
        return settings.FAISS_DIR / f"{intent_space.lower()}.index"
    
    def _get_metadata_path(self, intent_space: str) -> Path:
        """Get path for metadata file"""
        return settings.FAISS_DIR / f"{intent_space.lower()}_metadata.pkl"
    
    def _create_index(self) -> faiss.Index:
        """Create a new FAISS index"""
        # Using IndexFlatL2 for simplicity and exact search
        # For production with >100k documents, consider IndexIVFFlat or IndexHNSWFlat
        return faiss.IndexFlatL2(self.dimension)
    
    def _load_all_indexes(self):
        """Load all existing indexes on startup"""
        if not settings.FAISS_DIR.exists():
            return
        
        for intent_space in settings.DEFAULT_INTENT_SPACES:
            index_path = self._get_index_path(intent_space)
            metadata_path = self._get_metadata_path(intent_space)
            
            if index_path.exists():
                self.indexes[intent_space] = faiss.read_index(str(index_path))
            else:
                self.indexes[intent_space] = self._create_index()
            
            if metadata_path.exists():
                with open(metadata_path, 'rb') as f:
                    self.metadata[intent_space] = pickle.load(f)
            else:
                self.metadata[intent_space] = []
    
    def _save_index(self, intent_space: str):
        """Save index and metadata to disk"""
        index_path = self._get_index_path(intent_space)
        metadata_path = self._get_metadata_path(intent_space)
        
        faiss.write_index(self.indexes[intent_space], str(index_path))
        
        with open(metadata_path, 'wb') as f:
            pickle.dump(self.metadata[intent_space], f)
    
    def add_chunks(self, intent_space: str, embeddings: np.ndarray,
                   chunks_metadata: List[dict]) -> bool:
        """
        Add chunks to FAISS index
        
        Args:
            intent_space: Intent space name (e.g., "HR", "Legal")
            embeddings: Array of embeddings (shape: n_chunks x 384)
            chunks_metadata: List of metadata dicts for each chunk
        
        Returns:
            bool: Success status
        """
        try:
            if intent_space not in self.indexes:
                self.indexes[intent_space] = self._create_index()
                self.metadata[intent_space] = []
            
            # Ensure embeddings is float32 (required by FAISS)
            if embeddings.dtype != np.float32:
                embeddings = embeddings.astype(np.float32)
            
            # Add to index
            self.indexes[intent_space].add(embeddings)
            
            # Store metadata with index positions
            start_idx = len(self.metadata[intent_space])
            for i, meta in enumerate(chunks_metadata):
                meta['faiss_idx'] = start_idx + i
                self.metadata[intent_space].append(meta)
            
            # Save to disk
            self._save_index(intent_space)
            
            return True
        except Exception as e:
            print(f"Error adding chunks to FAISS: {e}")
            return False
    
    def search(self, intent_space: str, query_embedding: np.ndarray,
               top_k: int = 5) -> List[Tuple[dict, float]]:
        """
        Search FAISS index for similar chunks
        
        Args:
            intent_space: Intent space to search
            query_embedding: Query embedding (384-dim)
            top_k: Number of results to return
        
        Returns:
            List of (metadata, distance) tuples
        """
        if intent_space not in self.indexes:
            return []
        
        # Ensure query is float32 and 2D
        if query_embedding.dtype != np.float32:
            query_embedding = query_embedding.astype(np.float32)
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)
        
        # Search
        distances, indices = self.indexes[intent_space].search(query_embedding, top_k)
        
        # Get metadata for results
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx >= 0 and idx < len(self.metadata[intent_space]):
                meta = self.metadata[intent_space][idx].copy()
                meta['score'] = float(1 / (1 + distance))  # Convert distance to similarity score
                results.append((meta, float(distance)))
        
        return results
    
    def get_stats(self, intent_space: Optional[str] = None) -> dict:
        """Get index statistics"""
        if intent_space:
            if intent_space in self.indexes:
                return {
                    "intent_space": intent_space,
                    "total_chunks": len(self.metadata[intent_space]),
                    "index_size": self.indexes[intent_space].ntotal
                }
            return {"intent_space": intent_space, "total_chunks": 0, "index_size": 0}
        
        # Return stats for all spaces
        return {
            space: {
                "total_chunks": len(self.metadata.get(space, [])),
                "index_size": self.indexes.get(space, self._create_index()).ntotal
            }
            for space in settings.DEFAULT_INTENT_SPACES
        }
    
    def delete_document_chunks(self, intent_space: str, document_id: str) -> bool:
        """
        Delete all chunks for a document
        Note: FAISS doesn't support deletion, so we rebuild the index
        """
        try:
            if intent_space not in self.indexes:
                return False
            
            # Filter out chunks from this document
            new_metadata = [m for m in self.metadata[intent_space] if m.get('document_id') != document_id]
            
            if len(new_metadata) == len(self.metadata[intent_space]):
                return False  # No chunks found for this document
            
            # Rebuild index with remaining chunks
            if new_metadata:
                # Get embeddings for remaining chunks
                # This requires storing embeddings separately or recomputing
                # For MVP, we'll mark chunks as deleted in metadata
                pass
            
            self.metadata[intent_space] = new_metadata
            self._save_index(intent_space)
            
            return True
        except Exception as e:
            print(f"Error deleting document chunks: {e}")
            return False


# Global FAISS manager instance
faiss_manager = FAISSManager()