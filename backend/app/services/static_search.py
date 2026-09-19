import json
from functools import lru_cache
from pathlib import Path

from app.schemas.search import SearchResult
from app.services.search_provider import SearchProvider

DOCUMENTS_PATH = Path(__file__).resolve().parent.parent / "data" / "documents.json"


@lru_cache
def load_static_documents() -> tuple[SearchResult, ...]:
    raw = json.loads(DOCUMENTS_PATH.read_text(encoding="utf-8"))
    return tuple(SearchResult.model_validate(item) for item in raw)


class StaticSearchProvider(SearchProvider):
    """Returns the static document catalog. Azure Search will replace this later."""

    def __init__(self, documents: tuple[SearchResult, ...] | None = None) -> None:
        self._documents = documents if documents is not None else load_static_documents()

    async def search(self, query: str, top: int) -> list[SearchResult]:
        if not query.strip():
            return []
        return list(self._documents[:top])
