from fastapi.testclient import TestClient

from app.api.routes import search as search_routes
from app.main import create_app
from app.schemas.search import SearchResponse, SearchResult


class _FakeSearchService:
    async def search(self, query: str) -> SearchResponse:
        return SearchResponse(
            query=query,
            results=[
                SearchResult(
                    id="1",
                    title="Denied Claims Procedure",
                    content="If a claim is denied because of missing documentation...",
                    source="Claims-SOP-2026.pdf",
                    category="SOP",
                    score=0.92,
                )
            ],
        )

    async def close(self) -> None:
        return None


def test_search_rejects_empty_query() -> None:
    with TestClient(create_app()) as client:
        response = client.post("/api/search", json={"query": ""})
    assert response.status_code == 422


def test_search_rejects_missing_query() -> None:
    with TestClient(create_app()) as client:
        response = client.post("/api/search", json={})
    assert response.status_code == 422


def test_search_uses_mock_provider_when_configured() -> None:
    with TestClient(create_app()) as client:
        response = client.post("/api/search", json={"query": "denied claims procedure"})
    assert response.status_code == 200
    body = response.json()
    assert body["results"]
    assert "title" in body["results"][0]
    assert "content" in body["results"][0]
    assert "source" in body["results"][0]


def test_search_returns_results() -> None:
    app = create_app()
    app.dependency_overrides[search_routes.get_search_service] = lambda: _FakeSearchService()
    with TestClient(app) as client:
        response = client.post("/api/search", json={"query": "What is the procedure for denied claims?"})
    assert response.status_code == 200
    body = response.json()
    assert body["query"] == "What is the procedure for denied claims?"
    assert body["results"][0]["title"] == "Denied Claims Procedure"
    assert body["results"][0]["source"] == "Claims-SOP-2026.pdf"
