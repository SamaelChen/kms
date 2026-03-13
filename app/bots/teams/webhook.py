"""Teams webhook endpoint"""
from fastapi import APIRouter, Request, HTTPException
from botbuilder.schema import Activity

from app.bots.teams.bot import teams_bot

router = APIRouter()


@router.post("/teams")
async def teams_webhook(request: Request):
    """Handle Teams webhook updates"""
    try:
        activity = Activity().deserialize(await request.json())
        # Process activity using bot framework adapter
        # This requires proper adapter setup with Azure Bot Service
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(500, f"Webhook processing failed: {str(e)}")