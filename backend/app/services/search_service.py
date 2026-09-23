import logging

from app.core.config import Settings
from app.core.exceptions import SearchConfigurationError, SearchServiceError, http_error_from_search_exception
from app.db.database import get_session_factory
from app.schemas.search import SearchResponse, SearchResult
from app.services.azure_search import AzureSearchProvider
from app.services.mock_search import MockSearchProvider
from app.services.postgres_search import PostgresSearchProvider
from app.services.search_provider import SearchProvider

logger = logging.getLogger(__name__)


class SearchService:
    """Search orchestration. Selects mock, postgres, or Azure from SEARCH_PROVIDER."""

    def __init__(self, settings: Settings, provider: SearchProvider | None = None) -> None:
        self._settings = settings
        self._provider = provider or build_search_provider(settings)

    @property
    def provider_name(self) -> str:
        return self._settings.search_provider

    async def search(self, query: str) -> SearchResponse:
        logger.info('Search request received: query="%s"', query)
        logger.info("Search provider: %s", self.provider_name)
        try:
            results: list[SearchResult] = await self._provider.search(
                query=query,
                top=self._settings.azure_search_top,
            )
        except SearchServiceError as exc:
            logger.error("Search failed using provider %s: %s", self.provider_name, type(exc).__name__)
            raise http_error_from_search_exception(exc) from exc

        if self.provider_name == "azure":
            logger.info("Azure AI Search returned %s results", len(results))
        elif self.provider_name == "postgres":
            logger.info("PostgreSQL search returned %s results", len(results))
        else:
            logger.info("Mock search returned %s results", len(results))
        return SearchResponse(query=query, total=len(results), results=results)

    async def ping(self) -> None:
        await self._provider.ping()

    async def close(self) -> None:
        closer = getattr(self._provider, "close", None)
        if closer is not None:
            await closer()


def build_search_provider(settings: Settings) -> SearchProvider:
    if settings.search_provider == "azure":
        logger.info("Using Azure AI Search provider")
        return AzureSearchProvider(settings)
    if settings.search_provider == "postgres":
        session_factory = get_session_factory()
        if session_factory is None:
            raise SearchConfigurationError("PostgreSQL is not configured.")
        logger.info("Using PostgreSQL search provider")
        return PostgresSearchProvider(session_factory)
    logger.info("Using mock search provider")
    return MockSearchProvider()
