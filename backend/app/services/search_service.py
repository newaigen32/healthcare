import logging

from app.core.config import Settings
from app.core.exceptions import SearchServiceError, http_error_from_search_exception
from app.schemas.search import SearchResponse, SearchResult
from app.services.mock_search import MockSearchProvider
from app.services.search_provider import SearchProvider

logger = logging.getLogger(__name__)


class SearchService:
    """Search orchestration. Mock today; Azure AI Search can replace the provider later."""

    def __init__(self, settings: Settings, provider: SearchProvider | None = None) -> None:
        self._settings = settings
        self._provider = provider or MockSearchProvider()

    async def search(self, query: str) -> SearchResponse:
        logger.info("Search request received")
        try:
            results: list[SearchResult] = await self._provider.search(
                query=query,
                top=self._settings.azure_search_top,
            )
        except SearchServiceError as exc:
            logger.error("Search failed: %s", type(exc).__name__)
            raise http_error_from_search_exception(exc) from exc

        logger.info("Search completed", extra={"result_count": len(results)})
        return SearchResponse(query=query, total=len(results), results=results)

    async def close(self) -> None:
        closer = getattr(self._provider, "close", None)
        if closer is not None:
            await closer()
