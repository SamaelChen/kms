"""FastAPI main application"""
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.db.database import init_db
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    await init_db()
    yield
    # Shutdown
    pass


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