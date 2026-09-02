"""API health endpoint tests."""

from fastapi.testclient import TestClient

from app.main import app


def test_health_check_returns_service_metadata() -> None:
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "CareerPilot AI",
        "version": "0.1.0",
        "environment": "development",
    }

