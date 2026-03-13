"""Pydantic models for analytics"""
from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel


class DocumentMetrics(BaseModel):
    document_id: str
    document_name: str
    access_count: int
    last_accessed: Optional[datetime]


class IntentMetrics(BaseModel):
    intent_space: str
    query_count: int
    average_confidence: float


class TimeSeriesPoint(BaseModel):
    timestamp: datetime
    value: int


class AnalyticsSummary(BaseModel):
    total_documents: int
    total_queries: int
    queries_today: int
    average_response_time_ms: float
    average_confidence: float
    top_intents: List[IntentMetrics]
    top_documents: List[DocumentMetrics]
    query_volume_last_7_days: List[TimeSeriesPoint]


class HealthCheck(BaseModel):
    status: str
    version: str
    uptime_seconds: float
    database_connected: bool
    faiss_loaded: bool
    ollama_available: bool