"""Test configuration module"""
import pytest
from app.config import settings


def test_settings_loaded():
    """Test settings are loaded correctly"""
    assert settings is not None
    assert settings.LLM_MODEL == "qwen3.5:9b"
    assert settings.EMBEDDING_MODEL == "sentence-transformers/all-MiniLM-L6-v2"
    assert settings.CHUNK_SIZE == 1000
    assert settings.CHUNK_OVERLAP == 200


def test_intent_spaces():
    """Test default intent spaces"""
    assert "HR" in settings.DEFAULT_INTENT_SPACES
    assert "Legal" in settings.DEFAULT_INTENT_SPACES
    assert "Finance" in settings.DEFAULT_INTENT_SPACES
    assert "General" in settings.DEFAULT_INTENT_SPACES


def test_paths_exist():
    """Test data directories are configured"""
    assert settings.UPLOAD_DIR is not None
    assert settings.FAISS_DIR is not None
