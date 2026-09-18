from fastapi import APIRouter, Depends

from app.schemas.search import SearchRequest, SearchResponse
from app.services.search_service import SearchService

router = APIRouter(prefix="/api", tags=["search"])


def get_search_service() -> SearchService:
    raise RuntimeError("Search service dependency is not configured.")


@router.post("/search", response_model=SearchResponse)
async def search(
    payload: SearchRequest,
    search_service: SearchService = Depends(get_search_service),
) -> SearchResponse:
    return await search_service.search(query=payload.query.strip())
