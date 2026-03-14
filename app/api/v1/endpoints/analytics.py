"""Analytics endpoints"""
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.crud import QueryLogCRUD
from app.models.analytics import QueryStats, QueryLogEntry

router = APIRouter()


@router.get("/stats", response_model=QueryStats)
async def get_stats(db: AsyncSession = Depends(get_db)):
    stats = await QueryLogCRUD.get_stats(db)
    return QueryStats(**stats)


@router.get("/queries", response_model=List[QueryLogEntry])
async def get_recent_queries(limit: int = 100, db: AsyncSession = Depends(get_db)):
    logs = await QueryLogCRUD.get_recent(db, limit=limit)
    result = []
    for log in logs:
        log_id_val = log.id
        log_id = int(log_id_val) if log_id_val is not None else 0
        
        query_text_val = log.query_text
        query_text = str(query_text_val) if query_text_val is not None else ""
        
        intent_val = log.intent_classified
        intent = str(intent_val) if intent_val is not None else ""
        
        confidence_val = log.confidence_score
        confidence = float(confidence_val) if confidence_val is not None else 0.0
        
        response_text_val = log.response_text
        response_text = str(response_text_val) if response_text_val is not None else None
        
        response_time_val = log.response_time_ms
        response_time = float(response_time_val) if response_time_val is not None else None
        
        success_val = log.success
        success = bool(success_val) if success_val is not None else False
        
        frontend_val = log.frontend
        frontend = str(frontend_val) if frontend_val is not None else None
        
        created_val = log.created_at
        created = created_val if isinstance(created_val, datetime) else datetime.utcnow()
        
        result.append(QueryLogEntry(
            id=log_id,
            query_text=query_text,
            intent_classified=intent,
            confidence_score=confidence,
            response_text=response_text,
            response_time_ms=response_time,
            success=success,
            frontend=frontend,
            created_at=created
        ))
    return result