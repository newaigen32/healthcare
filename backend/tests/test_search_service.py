from typing import Any

import pytest

from app.core.config import Settings
from app.core.exceptions import SearchAuthenticationError, SearchUpstreamError
from app.services.azure_search import AzureSearchProvider
from app.services.mock_search import MockSearchProvider
from app.services.search_service import SearchService


class _FakeResults:
    def __init__(self, items: list[dict[str, Any]]) -> None:
        self._items = items

    def __aiter__(self):
        async def _gen():
            for item in self._items:
                yield item

        return _gen()


class _FakeSearchClient:
    def __init__(self, items: list[dict[str, Any]] | None = None, error: Exception | None = None) -> None:
        self.items = items or []
        self.error = error
        self.last_kwargs: dict[str, Any] | None = None
        self.closed = False

    async def search(self, **kwargs: Any):
        self.last_kwargs = kwargs
        if self.error:
            raise self.error
        return _FakeResults(self.items)

    async def close(self) -> None:
        self.closed = True


def _azure_settings(**overrides: Any) -> Settings:
    values = {
        "search_mode": "azure",
        "azure_search_endpoint": "https://example.search.windows.net",
        "azure_search_index_name": "knowledge-index",
        "azure_search_api_key": "test-key",
        "azure_search_vector_field": "",
    }
    values.update(overrides)
    return Settings(**values)


@pytest.mark.asyncio
async def test_mock_search_returns_matching_documents() -> None:
    provider = MockSearchProvider()
    results = await provider.search("denied claim procedure", top=5)
    assert results
    assert results[0].title == "Denied Claims Procedure"


@pytest.mark.asyncio
async def test_azure_provider_maps_documents() -> None:
    provider = AzureSearchProvider(_azure_settings())
    fake_client = _FakeSearchClient(
        items=[
            {
                "id": "document-id",
                "title": "Denied Claims Procedure",
                "content": "If a claim is denied because of missing documentation...",
                "source": "Claims-SOP.pdf",
                "category": "SOP",
                "@search.score": 0.92,
            }
        ]
    )
    provider._client = fake_client  # type: ignore[assignment]

    results = await provider.search("denied claims", top=5)
    assert len(results) == 1
    assert results[0].id == "document-id"
    assert results[0].title == "Denied Claims Procedure"
    assert results[0].content.startswith("If a claim is denied")
    assert results[0].source == "Claims-SOP.pdf"
    assert results[0].category == "SOP"
    assert results[0].score == 0.92
    assert fake_client.last_kwargs is not None
    assert fake_client.last_kwargs["search_text"] == "denied claims"
    assert "vector_queries" not in fake_client.last_kwargs


@pytest.mark.asyncio
async def test_azure_provider_uses_hybrid_when_vector_field_configured() -> None:
    provider = AzureSearchProvider(_azure_settings(azure_search_vector_field="contentVector"))
    fake_client = _FakeSearchClient(items=[])
    provider._client = fake_client  # type: ignore[assignment]
    await provider.search("denied claims", top=3)
    assert fake_client.last_kwargs is not None
    assert "vector_queries" in fake_client.last_kwargs


@pytest.mark.asyncio
async def test_azure_provider_maps_authentication_errors() -> None:
    from azure.core.exceptions import ClientAuthenticationError

    provider = AzureSearchProvider(_azure_settings())
    fake_client = _FakeSearchClient(error=ClientAuthenticationError("denied"))
    provider._client = fake_client  # type: ignore[assignment]
    with pytest.raises(SearchAuthenticationError):
        await provider.search("denied claims", top=5)


@pytest.mark.asyncio
async def test_search_service_returns_api_model() -> None:
    settings = Settings(search_mode="mock", azure_search_top=2)
    service = SearchService(settings, provider=MockSearchProvider())
    response = await service.search("denied claims")
    assert response.query == "denied claims"
    assert len(response.results) <= 2
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
