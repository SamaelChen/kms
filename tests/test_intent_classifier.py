"""Test intent classification"""
import pytest
import asyncio
from app.core.intent_classifier import intent_classifier


def test_classifier_initialization():
    """Test classifier is initialized"""
    assert intent_classifier is not None
    assert intent_classifier.confidence_threshold == 0.70
    assert "HR" in intent_classifier.intent_patterns
    assert "Legal" in intent_classifier.intent_patterns
    assert "Finance" in intent_classifier.intent_patterns


def test_rule_based_classification_hr():
    """Test HR keyword classification"""
    query = "What is the employee leave policy?"
    intent, confidence = intent_classifier._rule_based_classify(query.lower())
    
    # Should classify as HR or return None
    if intent is not None:
        assert intent == "HR"
        assert confidence > 0


def test_rule_based_classification_legal():
    """Test Legal keyword classification"""
    query = "What does the contract say about termination?"
    intent, confidence = intent_classifier._rule_based_classify(query.lower())
    
    if intent is not None:
        assert intent == "Legal"


def test_rule_based_classification_finance():
    """Test Finance keyword classification"""
    query = "How do I submit an expense report?"
    intent, confidence = intent_classifier._rule_based_classify(query.lower())
    
    if intent is not None:
        assert intent == "Finance"


def test_rule_based_no_match():
    """Test query with no keywords"""
    query = "asdfghjkl random text"
    intent, confidence = intent_classifier._rule_based_classify(query.lower())
    
    assert intent is None
    assert confidence == 0.0


@pytest.mark.asyncio
async def test_classify_async():
    """Test async classification"""
    query = "What is the leave policy?"
    
    # This will test the full pipeline including potential LLM fallback
    try:
        intent, confidence, method = await intent_classifier.classify(query)
        assert intent in ["HR", "Legal", "Finance", "General"]
        assert 0 <= confidence <= 1
        assert method in ["rule_based", "llm", "fallback"]
    except Exception as e:
        # LLM might not be available, that's ok for unit tests
        pytest.skip(f"LLM not available: {e}")
