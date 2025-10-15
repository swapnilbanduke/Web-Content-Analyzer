"""
Test API Endpoints
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


@pytest.mark.asyncio
async def test_analyze_invalid_url():
    """Test analyze endpoint with invalid URL"""
    response = client.post(
        "/api/v1/analyze",
        json={
            "url": "not-a-valid-url",
            "include_llm_analysis": False
        }
    )
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_analyze_missing_url():
    """Test analyze endpoint with missing URL"""
    response = client.post(
        "/api/v1/analyze",
        json={
            "include_llm_analysis": False
        }
    )
    assert response.status_code == 422  # Validation error
