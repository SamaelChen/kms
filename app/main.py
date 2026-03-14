"""FastAPI main application"""
import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.db.database import init_db
from app.api.v1.router import api_router
from app.core.startup import download_llm_model
from app.core.response_generator import response_generator
from app.core.intent_classifier import intent_classifier


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    
    # Download LLM model in background (don't block startup)
    asyncio.create_task(download_llm_model())
    
    yield
    
    # Shutdown
    await response_generator.close()
    await intent_classifier.close()


app = FastAPI(
    title="IntelliKnow KMS",
    description="Gen AI-powered Knowledge Management System",
    version="1.0.0",
    lifespan=lifespan
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "IntelliKnow KMS",
        "version": "1.0.0",
        "docs": "/docs"
    }