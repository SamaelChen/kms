"""
IntelliKnow KMS - Database Module
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, Boolean
from datetime import datetime

from app.config import settings

# Create async engine
engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True
)

# Create async session
AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False
)

# Base class for models
Base = declarative_base()


class Document(Base):
    """Document model for metadata storage"""
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String, nullable=False)  # pdf, docx
    intent_space = Column(String, nullable=False, default="General")
    status = Column(String, nullable=False, default="pending")  # pending, processing, completed, error
    chunk_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    error_message = Column(Text, nullable=True)


class QueryLog(Base):
    """Query log for analytics"""
    __tablename__ = "query_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    query_text = Column(Text, nullable=False)
    intent_classified = Column(String, nullable=False)
    confidence_score = Column(Float, nullable=False)
    response_text = Column(Text, nullable=True)
    source_documents = Column(Text, nullable=True)  # JSON array of document IDs
    response_time_ms = Column(Float, nullable=True)
    frontend = Column(String, nullable=True)  # telegram, teams, api
    user_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    success = Column(Boolean, default=True)


class IntentSpace(Base):
    """Intent space configuration"""
    __tablename__ = "intent_spaces"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    keywords = Column(Text, nullable=True)  # JSON array of keywords
    document_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    """Get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()