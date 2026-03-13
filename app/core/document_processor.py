"""Document processing module for parsing and chunking"""
import os
import re
import uuid
from pathlib import Path
from typing import List, Tuple
import shutil

from pypdf import PdfReader
from docx import Document as DocxDocument

from app.config import settings


class DocumentProcessor:
    """Process documents: parse, chunk, and prepare for embedding"""
    
    def __init__(self):
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP
    
    def parse_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            reader = PdfReader(file_path)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
        except Exception as e:
            raise ValueError(f"Failed to parse PDF: {e}")
        return text.strip()
    
    def parse_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        text = ""
        try:
            doc = DocxDocument(file_path)
            for para in doc.paragraphs:
                if para.text.strip():
                    text += para.text + "\n"
        except Exception as e:
            raise ValueError(f"Failed to parse DOCX: {e}")
        return text.strip()
    
    def parse_document(self, file_path: str, file_type: str) -> str:
        """Parse document based on file type"""
        if file_type.lower() == "pdf":
            return self.parse_pdf(file_path)
        elif file_type.lower() == "docx":
            return self.parse_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    def chunk_text(self, text: str, document_id: str) -> List[dict]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Full document text
            document_id: Document ID for metadata
        
        Returns:
            List of chunk dictionaries with text and metadata
        """
        chunks = []
        
        # Split text into words for token estimation
        words = text.split()
        
        # Estimate tokens (rough: 1 word ≈ 1.3 tokens for English)
        tokens_per_chunk = self.chunk_size
        overlap_tokens = self.chunk_overlap
        
        # Convert token counts to word counts
        words_per_chunk = int(tokens_per_chunk / 1.3)
        words_overlap = int(overlap_tokens / 1.3)
        
        start_idx = 0
        chunk_idx = 0
        
        while start_idx < len(words):
            end_idx = min(start_idx + words_per_chunk, len(words))
            chunk_words = words[start_idx:end_idx]
            chunk_text = " ".join(chunk_words)
            
            # Clean up the chunk
            chunk_text = self._clean_chunk(chunk_text)
            
            if chunk_text:
                chunks.append({
                    "chunk_id": f"{document_id}_chunk_{chunk_idx}",
                    "document_id": document_id,
                    "text": chunk_text,
                    "start_pos": start_idx,
                    "end_pos": end_idx,
                    "chunk_index": chunk_idx
                })
                chunk_idx += 1
            
            # Move start position with overlap
            start_idx += words_per_chunk - words_overlap
            
            # Prevent infinite loop on very small documents
            if start_idx >= end_idx:
                break
        
        return chunks
    
    def _clean_chunk(self, text: str) -> str:
        """Clean chunk text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove very short chunks (less than 50 characters)
        if len(text) < 50:
            return ""
        return text.strip()
    
    async def save_upload(self, file_content: bytes, filename: str) -> Tuple[str, str, int]:
        """
        Save uploaded file and return path info
        
        Args:
            file_content: Raw file bytes
            filename: Original filename
        
        Returns:
            Tuple of (document_id, file_path, file_size)
        """
        # Generate unique document ID
        document_id = str(uuid.uuid4())
        
        # Determine file extension
        file_ext = Path(filename).suffix.lower()
        if file_ext not in ['.pdf', '.docx']:
            raise ValueError(f"Unsupported file extension: {file_ext}")
        
        # Create safe filename
        safe_filename = f"{document_id}{file_ext}"
        file_path = settings.UPLOAD_DIR / safe_filename
        
        # Save file
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        file_size = os.path.getsize(file_path)
        
        return document_id, str(file_path), file_size
    
    async def delete_upload(self, file_path: str) -> bool:
        """Delete uploaded file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        except Exception:
            pass
        return False


# Global processor instance
document_processor = DocumentProcessor()