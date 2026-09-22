from typing import Any

import pytest

from app.core.config import Settings
from app.core.exceptions import SearchAuthenticationError, SearchUpstreamError
from app.services.azure_search import AzureSearchProvider, map_azure_document


class _FakeResults:
    def __init__(self, items: list[dict[str, Any]]) -> None:
        self._items = items

    def __aiter__(self):
        async def _gen():
            for item in self._items:
                yield item

        return _gen()


class _FakeSearchClient:
    def __init__(
        self,
        items: list[dict[str, Any]] | None = None,
        error: Exception | None = None,
        ping_error: Exception | None = None,
    ) -> None:
        self.items = items or []
        self.error = error
        self.ping_error = ping_error
        self.last_kwargs: dict[str, Any] | None = None
        self.closed = False

    async def search(self, **kwargs: Any):
        self.last_kwargs = kwargs
        if self.error:
            raise self.error
        return _FakeResults(self.items)

    async def get_document_count(self) -> int:
        if self.ping_error:
            raise self.ping_error
        return len(self.items)

    async def close(self) -> None:
        self.closed = True


def _azure_settings(**overrides: Any) -> Settings:
    values = {
        "search_provider": "azure",
        "azure_search_endpoint": "https://example.search.windows.net",
        "azure_search_index_name": "knowledge-index",
        "azure_search_api_key": "test-key",
    }
    values.update(overrides)
    return Settings(**values)


def test_map_azure_document_uses_configured_fields() -> None:
    settings = _azure_settings()
    result = map_azure_document(
        {
            "id": "document-id",
            "title": "Denied Claims Procedure",
            "content": "If a claim is denied because of missing documentation...",
            "source": "Claims-SOP.pdf",
            "category": "SOP",
            "@search.score": 4.21,
        },
        settings,
    )
    assert result.id == "document-id"
    assert result.title == "Denied Claims Procedure"
    assert result.content.startswith("If a claim is denied")
    assert result.source == "Claims-SOP.pdf"
    assert result.category == "SOP"
    assert result.score == 4.21


def test_map_azure_document_handles_missing_optional_fields() -> None:
    settings = _azure_settings()
    result = map_azure_document({"chunk": "Body text", "metadata_storage_name": "file.pdf"}, settings)
    assert result.title == "Untitled document"
    assert result.content == "Body text"
    assert result.source == "file.pdf"
    assert result.category is None
    assert result.score is None


def test_map_azure_document_keeps_azure_bm25_score() -> None:
    settings = _azure_settings()
    result = map_azure_document({"id": "1", "title": "Doc", "@search.score": 12.5}, settings)
    assert result.score == 12.5


@pytest.mark.asyncio
async def test_azure_provider_keyword_search_maps_results() -> None:
    provider = AzureSearchProvider(
        _azure_settings(),
        client=_FakeSearchClient(
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
        ),
    )
    results = await provider.search("denied claims", top=5)
    assert len(results) == 1
    assert results[0].id == "document-id"
    assert results[0].title == "Denied Claims Procedure"


@pytest.mark.asyncio
async def test_azure_provider_search_kwargs_are_keyword_only() -> None:
    fake_client = _FakeSearchClient(items=[])
    provider = AzureSearchProvider(_azure_settings(), client=fake_client)
    await provider.search("denied claims", top=3)
    assert fake_client.last_kwargs is not None
    assert fake_client.last_kwargs["search_text"] == "denied claims"
    assert fake_client.last_kwargs["top"] == 3
    assert "vector_queries" not in fake_client.last_kwargs


@pytest.mark.asyncio
async def test_azure_provider_maps_authentication_errors() -> None:
    from azure.core.exceptions import ClientAuthenticationError

    provider = AzureSearchProvider(
        _azure_settings(),
        client=_FakeSearchClient(error=ClientAuthenticationError("denied")),
    )
    with pytest.raises(SearchAuthenticationError):
        await provider.search("denied claims", top=5)


@pytest.mark.asyncio
async def test_azure_provider_maps_connection_errors() -> None:
    from azure.core.exceptions import ServiceRequestError

    provider = AzureSearchProvider(
        _azure_settings(),
        client=_FakeSearchClient(error=ServiceRequestError("offline")),
    )
    with pytest.raises(SearchUpstreamError):
        await provider.search("denied claims", top=5)
