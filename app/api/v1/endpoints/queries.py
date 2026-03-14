"""Query endpoints"""
import logging
from fastapi import APIRouter, HTTPException

from app.core.query_orchestrator import query_orchestrator
from app.models.query import QueryRequest, QueryResponse

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    try:
        response = await query_orchestrator.process(request)
        return response
    except ValueError as e:
        logger.warning(f"Invalid query request: {e}")
        raise HTTPException(400, str(e))
    except TimeoutError as e:
        logger.error(f"Query processing timeout: {e}")
        raise HTTPException(504, "Query processing timed out")
    except Exception as e:
        logger.error(f"Query processing failed: {e}")
        raise HTTPException(500, "Query processing failed")