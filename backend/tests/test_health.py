"""Automated tests for health check endpoints and error responses."""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_health_endpoint() -> None:
    """Verify that root /health endpoint returns 200 and structured health schema."""
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "phase" in data
    assert "capabilities" in data
    assert data["capabilities"]["health_check"] == "active"
    # Ensure Phase 2 core capabilities are active
    assert data["capabilities"]["repository_ingestion"] == "active"
    assert data["capabilities"]["ast_parsing"] == "active"
    assert data["capabilities"]["graph_visualization"] == "active"
    assert data["capabilities"]["source_code_search"] == "active"
    assert data["capabilities"]["ai_explanations"] == "active"


def test_v1_health_endpoint() -> None:
    """Verify that /api/v1/health endpoint returns 200 and matches the same structure."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert data["app_name"] == "RepoSense AI Backend"
    assert "timestamp" in data


def test_structured_404_error_response() -> None:
    """Verify that nonexistent endpoints return structured ErrorResponse format."""
    response = client.get("/nonexistent-endpoint-test")
    assert response.status_code == 404

    data = response.json()
    assert "error" in data
    assert data["code"] == "HTTP_404"
    assert "metadata" in data
