"""Pydantic models for documents"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class DocumentBase(BaseModel):
    filename: str
    file_type: str = Field(..., pattern="^(pdf|docx|txt|md|xlsx|pptx)$")
    intent_space: str = "General"


class DocumentCreate(DocumentBase):
    pass


class DocumentResponse(DocumentBase):
    id: str
    file_size: int
    status: str
    chunk_count: int = 0
    created_at: datetime
    updated_at: datetime
    error_message: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class DocumentChunk(BaseModel):
    chunk_id: str
    document_id: str
    text: str
    start_pos: int
    end_pos: int
    embedding: Optional[List[float]] = None


class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    status: str
    message: str


class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int