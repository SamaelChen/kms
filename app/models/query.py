"""Pydantic models for queries and responses"""
from datetime import datetime, timezone
from typing import List, Optional, Dict
from pydantic import BaseModel, Field, ConfigDict


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    user_id: Optional[str] = None
    frontend: Optional[str] = Field(None, pattern="^(telegram|teams|api)$")


class Citation(BaseModel):
    document_id: str
    document_name: str
    chunk_index: int
    text_preview: str


class QueryResponse(BaseModel):
    query: str
    response: str
    intent_classified: str
    confidence_score: float
    citations: List[Citation]
    response_time_ms: float
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class QueryLogEntry(BaseModel):
    id: int
    query_text: str
    intent_classified: str
    confidence_score: float
    response_text: Optional[str]
    source_documents: Optional[str]
    response_time_ms: Optional[float]
    frontend: Optional[str]
    user_id: Optional[str]
    created_at: datetime
    success: bool
    
    model_config = ConfigDict(from_attributes=True)


class QueryStats(BaseModel):
    total_queries: int
    successful_queries: int
    average_confidence: float
    average_response_time_ms: float