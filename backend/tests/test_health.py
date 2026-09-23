from fastapi.testclient import TestClient

from app.api.routes import health as health_routes
from app.core.exceptions import SearchUpstreamError
from app.main import create_app


class _FailingSearchService:
    async def ping(self) -> None:
        raise SearchUpstreamError("offline")

    async def close(self) -> None:
        return None


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
    assert response.json() == {"status": "healthy", "provider": "mock", "connected": True}


def test_database_health_is_unavailable_without_database() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/health/database")
    assert response.status_code == 503
    assert response.json()["connected"] is False


def test_search_health_reports_azure_disconnect_without_secrets() -> None:
    app = create_app()
    app.dependency_overrides[health_routes.get_search_service] = lambda: _FailingSearchService()
    with TestClient(app) as client:
        response = client.get("/health/search")
    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "unavailable"
    assert body["connected"] is False
    assert "api_key" not in str(body).lower()
    assert "secret" not in str(body).lower()
