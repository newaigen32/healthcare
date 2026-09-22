from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "healthy"
    search_provider: str = "mock"


class SearchHealthResponse(BaseModel):
    status: str
    provider: str
    connected: bool
    index: str | None = None


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)


class SearchResult(BaseModel):
    id: str
    title: str
    content: str
    source: str
    category: str | None = None
    score: float | None = None


class SearchResponse(BaseModel):
    query: str
    total: int
    results: list[SearchResult]
