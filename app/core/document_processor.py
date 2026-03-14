"""
Document processor orchestrates parsing, chunking, embedding, and storage.
"""
import os
import uuid
from pathlib import Path
from typing import List, Tuple

from app.config import settings
from app.core.document_parser import DocumentParser
from app.core.chunker import TextChunker
from app.core.knowledge_base import knowledge_base
from app.db.crud import DocumentCRUD, DocumentChunkCRUD
from app.db.database import AsyncSessionLocal


class DocumentProcessor:
    def __init__(self):
        self.parser = DocumentParser()
        self.chunker = TextChunker()
    
    async def process(self, document_id: str, file_path: str, intent_space: str) -> dict:
        """Process a document through the complete pipeline."""
        try:
            async with AsyncSessionLocal() as db:
                await DocumentCRUD.update_status(db, document_id, "processing")
                document = await DocumentCRUD.get_by_id(db, document_id)
                if document is not None:
                    filename = str(document.filename)
                else:
                    filename = "Unknown"
            
            text = self.parser.parse(file_path)
            
            if not text or not text.strip():
                raise ValueError("Document contains no extractable text")
            
            chunks = self.chunker.chunk_text(text)
            
            if not chunks:
                raise ValueError("No chunks generated from document")
            
            chunk_ids = await self._store_chunks(document_id, filename, intent_space, chunks)
            
            async with AsyncSessionLocal() as db:
                await DocumentCRUD.update_status(
                    db, document_id, "completed", 
                    chunk_count=len(chunk_ids)
                )
            
            return {
                "success": True,
                "chunk_count": len(chunk_ids),
                "error": None
            }
            
        except Exception as e:
            error_msg = str(e)
            async with AsyncSessionLocal() as db:
                await DocumentCRUD.update_status(
                    db, document_id, "error", 
                    error_message=error_msg
                )
            
            return {
                "success": False,
                "chunk_count": 0,
                "error": error_msg
            }
    
    async def _store_chunks(
        self, 
        document_id: str, 
        filename: str,
        intent_space: str, 
        chunks: List[str]
    ) -> List[str]:
        chunk_ids = []
        chunk_data = []
        
        for idx, content in enumerate(chunks):
            chunk_id = str(uuid.uuid4())
            chunk_ids.append(chunk_id)
            
            token_count = self.chunker.estimate_tokens(content)
            
            async with AsyncSessionLocal() as db:
                await DocumentChunkCRUD.create(
                    db, chunk_id, document_id, intent_space, 
                    idx, content, token_count
                )
            
            chunk_data.append({
                "id": chunk_id,
                "text": content,
                "document_id": document_id,
                "document_name": filename,
                "chunk_index": idx
            })
        
        await knowledge_base.add_document_chunks(
            intent_space=intent_space,
            document_id=document_id,
            chunks=chunk_data
        )
        
        return chunk_ids
    
    async def reprocess(self, document_id: str, file_path: str, intent_space: str) -> dict:
        async with AsyncSessionLocal() as db:
            await DocumentChunkCRUD.delete_by_document(db, document_id)
        
        return await self.process(document_id, file_path, intent_space)
    
    async def save_upload(self, file_content: bytes, filename: str) -> Tuple[str, str, int]:
        document_id = str(uuid.uuid4())
        
        file_ext = Path(filename).suffix.lower()
        if not self.parser.is_supported(filename):
            raise ValueError(f"Unsupported file type: {file_ext}")
        
        safe_filename = f"{document_id}{file_ext}"
        file_path = settings.UPLOAD_DIR / safe_filename
        
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        file_size = os.path.getsize(file_path)
        
        return document_id, str(file_path), file_size
    
    async def delete_upload(self, file_path: str) -> bool:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        except Exception:
            pass
        return False


document_processor = DocumentProcessor()
