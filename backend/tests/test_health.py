from fastapi.testclient import TestClient

from app.main import create_app


def test_health_returns_healthy() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert body["search_provider"] == "mock"


def test_search_health_returns_healthy_for_mock() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/health/search")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "search_provider": "mock"}
