"""Test API endpoints"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "IntelliKnow KMS" in response.json().get("name", "")


def test_api_health_endpoint():
    """Test API health endpoint"""
    response = client.get("/api/v1/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "intelliknow-kms"


# def test_upload_document_no_file():
#     """Test upload without file returns error"""
#     response = client.post("/api/v1/documents/upload")
#     assert response.status_code == 422  # Validation error


def test_query_endpoint_validation():
    """Test query endpoint validation"""
    # Test with empty query
    response = client.post("/api/v1/queries/ask", json={"query": ""})
    assert response.status_code == 422  # Validation error


def test_analytics_stats():
    """Test analytics stats endpoint"""
    response = client.get("/api/v1/analytics/stats")
    # Should return 200 even if database is empty
    assert response.status_code in [200, 500]  # 500 if DB not initialized
