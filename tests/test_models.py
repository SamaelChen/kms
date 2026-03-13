"""Test Pydantic models"""
import pytest
from datetime import datetime
from app.models.document import DocumentCreate, DocumentResponse
from app.models.query import QueryRequest, QueryResponse, Citation
from app.models.intent import IntentSpaceCreate


def test_document_create():
    """Test document creation model"""
    doc = DocumentCreate(
        filename="test.pdf",
        file_type="pdf",
        intent_space="HR"
    )
    assert doc.filename == "test.pdf"
    assert doc.file_type == "pdf"
    assert doc.intent_space == "HR"


def test_query_request():
    """Test query request model"""
    query = QueryRequest(
        query="What is the leave policy?",
        user_id="123",
        frontend="telegram"
    )
    assert query.query == "What is the leave policy?"
    assert query.user_id == "123"
    assert query.frontend == "telegram"


def test_citation():
    """Test citation model"""
    citation = Citation(
        document_id="doc-123",
        document_name="HR_Policy.pdf",
        chunk_index=0,
        text_preview="Employees are entitled to..."
    )
    assert citation.document_id == "doc-123"
    assert citation.document_name == "HR_Policy.pdf"


def test_intent_space_create():
    """Test intent space creation"""
    space = IntentSpaceCreate(
        name="IT",
        description="IT Support",
        keywords=["computer", "network", "software"]
    )
    assert space.name == "IT"
    assert "computer" in space.keywords
