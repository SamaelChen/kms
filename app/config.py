"""
IntelliKnow KMS - Configuration Module
"""
import os
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )
    
    # Project paths
    BASE_DIR: Path = Path(__file__).parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    UPLOAD_DIR: Path = DATA_DIR / "uploads"
    FAISS_DIR: Path = DATA_DIR / "faiss"
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///data/sqlite/kms.db"
    
    # AI/LLM Configuration
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    LLM_MODEL: str = "qwen3.5:9b"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Intent Classification
    INTENT_CONFIDENCE_THRESHOLD: float = 0.70
    
    # Document Processing
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # Bot Tokens
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_WEBHOOK_URL: str = ""
    
    TEAMS_APP_ID: str = ""
    TEAMS_APP_PASSWORD: str = ""
    TEAMS_WEBHOOK_URL: str = ""
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # Admin Dashboard
    STREAMLIT_PORT: int = 8501
    
    # Security
    API_KEY: str = ""
    
    # Default Intent Spaces
    DEFAULT_INTENT_SPACES: List[str] = ["HR", "Legal", "Finance", "General"]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure data directories exist
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.FAISS_DIR.mkdir(parents=True, exist_ok=True)
        (self.DATA_DIR / "sqlite").mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()