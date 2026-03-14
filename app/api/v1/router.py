"""API router"""
from fastapi import APIRouter

from app.api.v1.endpoints import documents, queries, health, analytics, intents

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(queries.router, prefix="/queries", tags=["queries"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(intents.router, prefix="/intents", tags=["intents"])