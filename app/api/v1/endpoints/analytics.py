"""Analytics endpoints"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.crud import QueryLogCRUD
from app.models.analytics import QueryStats

router = APIRouter()


@router.get("/stats", response_model=QueryStats)
async def get_stats(db: AsyncSession = Depends(get_db)):
    """Get query statistics"""
    stats = await QueryLogCRUD.get_stats(db)
    return QueryStats(**stats)