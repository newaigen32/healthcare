from abc import ABC, abstractmethod

from app.schemas.search import SearchResult


class SearchProvider(ABC):
    @abstractmethod
    async def search(self, query: str, top: int) -> list[SearchResult]:
        raise NotImplementedError
