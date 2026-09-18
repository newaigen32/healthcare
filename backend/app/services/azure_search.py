from __future__ import annotations

import asyncio
import logging
from typing import Any

from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ServiceRequestError,
)
from azure.search.documents.aio import SearchClient
from azure.search.documents.models import VectorizableTextQuery

from app.core.config import Settings
from app.core.exceptions import (
    SearchAuthenticationError,
    SearchConfigurationError,
    SearchTimeoutError,
    SearchUpstreamError,
)
from app.schemas.search import SearchResult
from app.services.search_provider import SearchProvider

logger = logging.getLogger(__name__)


class AzureSearchProvider(SearchProvider):
    def __init__(self, settings: Settings) -> None:
        if not (
            settings.azure_search_endpoint
            and settings.azure_search_index_name
            and settings.azure_search_api_key
        ):
            raise SearchConfigurationError("Azure Search settings are incomplete.")

        self._settings = settings
        self._client: SearchClient | None = None

    def _get_client(self) -> SearchClient:
        if self._client is None:
            self._client = SearchClient(
                endpoint=self._settings.azure_search_endpoint,
                index_name=self._settings.azure_search_index_name,
                credential=AzureKeyCredential(self._settings.azure_search_api_key),
                connection_timeout=self._settings.azure_search_timeout_seconds,
                read_timeout=self._settings.azure_search_timeout_seconds,
            )
        return self._client

    async def close(self) -> None:
        if self._client is not None:
            await self._client.close()

    async def search(self, query: str, top: int) -> list[SearchResult]:
        search_kwargs = self._build_search_kwargs(query=query, top=top)
        mode = "hybrid" if self._settings.hybrid_search_enabled else "keyword"
        logger.info(
            "Azure Search request started",
            extra={"search_mode": mode, "top": top, "index": self._settings.azure_search_index_name},
        )

        try:
            results = await self._get_client().search(**search_kwargs)
            mapped: list[SearchResult] = []
            async for item in results:
                mapped.append(self._map_document(item))
            logger.info("Azure Search request completed", extra={"result_count": len(mapped)})
            return mapped
        except ClientAuthenticationError as exc:
            logger.error("Azure Search authentication failed")
            raise SearchAuthenticationError("Azure Search authentication failed.") from exc
        except (TimeoutError, asyncio.TimeoutError) as exc:
            logger.error("Azure Search timed out")
            raise SearchTimeoutError("Azure Search timed out.") from exc
        except ServiceRequestError as exc:
            logger.error("Azure Search connection failed: %s", type(exc).__name__)
            raise SearchUpstreamError("Azure Search connection failed.") from exc
        except HttpResponseError as exc:
            logger.error("Azure Search returned HTTP %s", getattr(exc, "status_code", "unknown"))
            raise SearchUpstreamError("Azure Search returned an unexpected response.") from exc
        except Exception as exc:  # pragma: no cover - defensive mapping
            logger.exception("Unexpected Azure Search error")
            raise SearchUpstreamError("Azure Search request failed.") from exc

    def _build_search_kwargs(self, query: str, top: int) -> dict[str, Any]:
        kwargs: dict[str, Any] = {
            "search_text": query,
            "top": top,
            "include_total_count": False,
        }

        if self._settings.hybrid_search_enabled:
            kwargs["vector_queries"] = [
                VectorizableTextQuery(
                    text=query,
                    k_nearest_neighbors=self._settings.azure_search_vector_k,
                    fields=self._settings.azure_search_vector_field,
                )
            ]

        if self._settings.azure_search_semantic_configuration:
            kwargs["query_type"] = "semantic"
            kwargs["semantic_configuration_name"] = self._settings.azure_search_semantic_configuration

        return kwargs

    def _map_document(self, document: dict[str, Any]) -> SearchResult:
        settings = self._settings
        document_id = _as_str(document.get(settings.azure_search_id_field) or document.get("id"))
        title = _as_str(document.get(settings.azure_search_title_field)) or "Untitled document"
        content = _as_str(
            document.get(settings.azure_search_content_field)
            or document.get("content")
            or document.get("chunk")
            or document.get("text")
        )
        source = _as_str(
            document.get(settings.azure_search_source_field)
            or document.get("metadata_storage_name")
            or document.get("sourcefile")
        )
        category_value = document.get(settings.azure_search_category_field)
        category = _as_str(category_value) if category_value not in (None, "") else None
        score_value = document.get("@search.score")
        score = float(score_value) if isinstance(score_value, (int, float)) else None

        return SearchResult(
            id=document_id or title,
            title=title,
            content=content,
            source=source or "Unknown source",
            category=category,
            score=score,
        )


def _as_str(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()
