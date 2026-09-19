import pytest

from app.core.config import Settings
from app.core.exceptions import SearchUpstreamError
from app.services.mock_search import MockSearchProvider
from app.services.search_service import SearchService


@pytest.mark.asyncio
async def test_mock_search_returns_matching_documents() -> None:
    provider = MockSearchProvider()
    results = await provider.search("What is SOP's", top=5)
    assert len(results) == 3
    assert results[0].title == "Denied Claims Procedure"
    assert results[0].id == "1"


@pytest.mark.asyncio
async def test_mock_search_returns_empty_when_nothing_matches() -> None:
    provider = MockSearchProvider()
    results = await provider.search("zzzznotfoundxyz", top=5)
    assert results == []


@pytest.mark.asyncio
async def test_search_service_returns_api_model_with_total() -> None:
    settings = Settings(search_mode="mock")
    service = SearchService(settings, provider=MockSearchProvider())
    response = await service.search("denied claims")
    assert response.query == "denied claims"
    assert response.total == len(response.results)
    assert response.total == 3
    assert response.results[0].title


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
