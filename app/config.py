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
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure data directories exist
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.FAISS_DIR.mkdir(parents=True, exist_ok=True)
        (self.DATA_DIR / "sqlite").mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()