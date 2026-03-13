"""Telegram webhook endpoint"""
from fastapi import APIRouter, Request, HTTPException

from app.bots.telegram.bot import telegram_bot

router = APIRouter()


@router.post("/telegram")
async def telegram_webhook(request: Request):
    """Handle Telegram webhook updates"""
    try:
        data = await request.json()
        await telegram_bot.process_webhook_update(data)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(500, f"Webhook processing failed: {str(e)}")