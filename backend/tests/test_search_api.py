from fastapi.testclient import TestClient

from app.main import create_app


def test_health() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert body["search_provider"] == "mock"


def test_search_rejects_empty_query() -> None:
    with TestClient(create_app()) as client:
        response = client.post("/api/search", json={"query": ""})
    assert response.status_code == 422


def test_search_rejects_missing_query() -> None:
    with TestClient(create_app()) as client:
        response = client.post("/api/search", json={})
    assert response.status_code == 422


def test_search_returns_static_documents() -> None:
    with TestClient(create_app()) as client:
        response = client.post("/api/search", json={"query": "What is SOP's"})
    assert response.status_code == 200
    body = response.json()
    assert body["query"] == "What is SOP's"
    assert body["total"] == 3
    assert [item["id"] for item in body["results"]] == ["1", "2", "3"]
    assert body["results"][0]["title"] == "Denied Claims Procedure"
    assert body["results"][0]["source"] == "Claims-SOP-2026.pdf"


def test_search_returns_the_same_static_catalog_for_any_query() -> None:
    with TestClient(create_app()) as client:
        response = client.post("/api/search", json={"query": "zzzznotfoundxyz"})
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 3
    assert len(body["results"]) == 3
