"""Integration tests for query processing pipeline"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from app.core.query_orchestrator import QueryOrchestrator
from app.core.intent_classifier import IntentClassifier
from app.models.query import QueryRequest, QueryResponse


@pytest.fixture
def orchestrator():
    return QueryOrchestrator()


@pytest.fixture
def classifier():
    return IntentClassifier()


@pytest.mark.asyncio
async def test_query_orchestrator_cache_behavior(orchestrator):
    request = QueryRequest(query="What is the leave policy?", frontend=None)
    
    with patch.object(orchestrator.intent_classifier, 'classify', 
                     return_value=("HR", 0.95, "leave policy")) as mock_classify, \
         patch.object(orchestrator.knowledge_base, 'search',
                     return_value=[]) as mock_search, \
         patch.object(orchestrator.response_generator, 'generate',
                     return_value="Test response") as mock_generate:
        
        response = await orchestrator.process(request)
        
        assert response.intent_classified == "HR"
        assert response.confidence_score == 0.95
        mock_classify.assert_called_once()


@pytest.mark.asyncio
async def test_intent_classifier_hr_keywords(classifier):
    """Test HR intent classification with various keywords"""
    test_cases = [
        ("What is the employee leave policy?", "HR"),
        ("How do I request vacation?", "HR"),
        ("Tell me about benefits", "HR"),
        ("What are my health insurance options?", "HR"),
    ]
    
    for query, expected_intent in test_cases:
        intent, confidence, matched = await classifier.classify(query)
        assert intent == expected_intent, f"Failed for: {query}"
        assert confidence > 0


@pytest.mark.asyncio
async def test_intent_classifier_legal_keywords(classifier):
    """Test Legal intent classification"""
    test_cases = [
        ("What does the contract say?", "Legal"),
        ("Termination clause details", "Legal"),
        ("Intellectual property rights", "Legal"),
    ]
    
    for query, expected_intent in test_cases:
        intent, confidence, matched = await classifier.classify(query)
        assert intent == expected_intent, f"Failed for: {query}"


@pytest.mark.asyncio
async def test_intent_classifier_finance_keywords(classifier):
    """Test Finance intent classification"""
    test_cases = [
        ("How do I submit expenses?", "Finance"),
        ("Budget approval process", "Finance"),
        ("Reimbursement policy", "Finance"),
    ]
    
    for query, expected_intent in test_cases:
        intent, confidence, matched = await classifier.classify(query)
        assert intent == expected_intent, f"Failed for: {query}"


@pytest.mark.asyncio
async def test_intent_classifier_low_confidence(classifier):
    """Test that low confidence queries default to General"""
    query = "asdfghjkl random text"
    intent, confidence, matched = await classifier.classify(query)
    
    assert intent == "General"
    assert confidence == 0.0


@pytest.mark.asyncio
async def test_query_orchestrator_response_time(orchestrator):
    request = QueryRequest(query="Test query", frontend=None)
    
    with patch.object(orchestrator.intent_classifier, 'classify',
                     return_value=("General", 0.5, "test")), \
         patch.object(orchestrator.knowledge_base, 'search',
                     return_value=[]), \
         patch.object(orchestrator.response_generator, 'generate',
                     return_value="Test"):
        
        response = await orchestrator.process(request)
        
        assert response.response_time_ms > 0
        assert response.query == "Test query"


def test_citation_building(orchestrator):
    """Test citation building from search results"""
    search_results = [
        ({
            "document_id": "doc-1",
            "document_name": "Policy.pdf",
            "chunk_index": 0,
            "text": "This is the full text of the policy document that explains the rules."
        }, 0.95),
        ({
            "document_id": "doc-1",  # Same doc, should be deduplicated
            "document_name": "Policy.pdf",
            "chunk_index": 1,
            "text": "Another chunk from the same document."
        }, 0.90),
        ({
            "document_id": "doc-2",
            "document_name": "Rules.pdf",
            "chunk_index": 0,
            "text": "Different document content here."
        }, 0.85),
    ]
    
    citations = orchestrator._build_citations(search_results)
    
    assert len(citations) == 2  # doc-1 and doc-2, not duplicated
    assert citations[0].document_id == "doc-1"
    assert citations[0].document_name == "Policy.pdf"
    assert citations[0].text_preview == "This is the full text of the policy document that explains the rul..."


@pytest.mark.asyncio
async def test_empty_query_handling(orchestrator):
    request = QueryRequest(query="", frontend=None)
    
    with pytest.raises(ValueError):
        await orchestrator.process(request)
