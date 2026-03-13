"""Test document processing"""
import pytest
from app.core.document_processor import document_processor


def test_document_processor_initialization():
    """Test document processor is initialized"""
    assert document_processor is not None
    assert document_processor.chunk_size == 1000
    assert document_processor.chunk_overlap == 200


def test_chunk_text():
    """Test text chunking"""
    text = "This is a test document. " * 100  # Create a long text
    chunks = document_processor.chunk_text(text, "doc-123")
    
    assert len(chunks) > 0
    assert all("chunk_id" in chunk for chunk in chunks)
    assert all("document_id" in chunk for chunk in chunks)
    assert all("text" in chunk for chunk in chunks)


def test_clean_chunk():
    """Test chunk cleaning"""
    # Test excessive whitespace removal
    dirty_text = "This    has   too    many   spaces"
    clean = document_processor._clean_chunk(dirty_text)
    assert "    " not in clean


def test_clean_chunk_short_text():
    """Test short text is filtered out"""
    short = "Hi"
    result = document_processor._clean_chunk(short)
    assert result == ""
