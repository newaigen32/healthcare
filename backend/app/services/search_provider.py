from abc import ABC, abstractmethod

from app.schemas.search import SearchResult


class SearchProvider(ABC):
    @abstractmethod
    async def search(self, query: str, top: int) -> list[SearchResult]:
        raise NotImplementedError

    async def ping(self) -> None:
        """Optional connectivity check. Mock providers no-op."""
        return None
