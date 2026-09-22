import pytest

from app.core.config import Settings
from app.core.exceptions import SearchConfigurationError, SearchUpstreamError
from app.schemas.search import SearchResult
from app.services.azure_search import AzureSearchProvider
from app.services.mock_search import MockSearchProvider
from app.services.search_service import SearchService, build_search_provider
from app.services.static_search import load_static_documents


def test_build_provider_selects_mock_by_default() -> None:
    settings = Settings(search_provider="mock")
    assert isinstance(build_search_provider(settings), MockSearchProvider)


def test_build_provider_selects_azure() -> None:
    settings = Settings(
        search_provider="azure",
        azure_search_endpoint="https://example.search.windows.net",
        azure_search_index_name="knowledge-index",
        azure_search_api_key="test-key",
    )
    assert isinstance(build_search_provider(settings), AzureSearchProvider)


def test_azure_provider_requires_credentials() -> None:
    settings = Settings(search_provider="azure")
    with pytest.raises(SearchConfigurationError):
        AzureSearchProvider(settings)


def test_search_mode_alias_still_selects_provider() -> None:
    settings = Settings.model_validate({"SEARCH_MODE": "mock"})
    assert settings.search_provider == "mock"


@pytest.mark.asyncio
async def test_mock_provider_returns_static_catalog() -> None:
    provider = MockSearchProvider()
    results = await provider.search("What is SOP's", top=5)
    assert len(results) == 3
    assert results[0].title == "Denied Claims Procedure"
    assert results[0].id == "1"


@pytest.mark.asyncio
async def test_search_service_returns_api_model_with_total() -> None:
    settings = Settings(search_provider="mock")
    service = SearchService(settings, provider=MockSearchProvider())
    response = await service.search("denied claims")
    assert response.query == "denied claims"
    assert response.total == 3
    assert response.results[0].title


@pytest.mark.asyncio
async def test_search_service_wraps_upstream_errors() -> None:
    class _FailingProvider:
        async def search(self, query: str, top: int):
            raise SearchUpstreamError("boom")

    settings = Settings(search_provider="mock")
    service = SearchService(settings, provider=_FailingProvider())  # type: ignore[arg-type]
    with pytest.raises(Exception) as exc_info:
        await service.search("denied claims")
    assert "couldn't complete the search" in str(exc_info.value.detail).lower()


def test_static_documents_are_typed_search_results() -> None:
    documents = load_static_documents()
    assert all(isinstance(document, SearchResult) for document in documents)
