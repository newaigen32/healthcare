import pytest

from app.core.config import Settings
from app.core.exceptions import SearchUpstreamError
from app.schemas.search import SearchResult
from app.services.search_service import SearchService
from app.services.static_search import StaticSearchProvider, load_static_documents


@pytest.mark.asyncio
async def test_static_search_returns_catalog_documents() -> None:
    provider = StaticSearchProvider()
    results = await provider.search("What is SOP's", top=5)
    assert len(results) == 3
    assert results[0].title == "Denied Claims Procedure"
    assert results[0].id == "1"
    assert load_static_documents()[0].source == "Claims-SOP-2026.pdf"


@pytest.mark.asyncio
async def test_static_search_honors_top() -> None:
    provider = StaticSearchProvider()
    results = await provider.search("anything", top=1)
    assert len(results) == 1


@pytest.mark.asyncio
async def test_search_service_returns_api_model_with_total() -> None:
    settings = Settings(search_mode="mock")
    service = SearchService(settings, provider=StaticSearchProvider())
    response = await service.search("denied claims")
    assert response.query == "denied claims"
    assert response.total == 3
    assert response.results[0].title


@pytest.mark.asyncio
async def test_search_service_can_return_empty_static_catalog() -> None:
    settings = Settings(search_mode="mock")
    empty = StaticSearchProvider(documents=tuple())
    service = SearchService(settings, provider=empty)
    response = await service.search("denied claims")
    assert response.total == 0
    assert response.results == []


@pytest.mark.asyncio
async def test_search_service_wraps_upstream_errors() -> None:
    class _FailingProvider:
        async def search(self, query: str, top: int):
            raise SearchUpstreamError("boom")

    settings = Settings(search_mode="mock")
    service = SearchService(settings, provider=_FailingProvider())  # type: ignore[arg-type]
    with pytest.raises(Exception) as exc_info:
        await service.search("denied claims")
    assert "couldn't complete the search" in str(exc_info.value.detail).lower()


def test_static_documents_are_typed_search_results() -> None:
    documents = load_static_documents()
    assert all(isinstance(document, SearchResult) for document in documents)
