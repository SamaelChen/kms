"""Pydantic models for intent spaces"""
from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class IntentSpaceBase(BaseModel):
    name: str
    description: Optional[str] = None
    keywords: List[str] = []


class IntentSpaceCreate(IntentSpaceBase):
    pass


class IntentSpaceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[List[str]] = None


class IntentSpaceResponse(IntentSpaceBase):
    id: str
    document_count: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class IntentClassification(BaseModel):
    query: str
    classified_intent: str
    confidence_score: float
    method: str  # rule_based, llm, fallback
    timestamp: datetime = datetime.now(timezone.utc)


class IntentSpaceList(BaseModel):
    spaces: List[IntentSpaceResponse]
    total: int