"""Query endpoints"""
from fastapi import APIRouter, HTTPException

from app.core.query_orchestrator import query_orchestrator
from app.models.query import QueryRequest, QueryResponse

router = APIRouter()


@router.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """Ask a question to the knowledge base"""
    try:
        response = await query_orchestrator.process(request)
        return response
    except Exception as e:
        raise HTTPException(500, f"Query processing failed: {str(e)}")