from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.schemas.search import HealthResponse, SearchHealthResponse
from app.services.search_service import SearchService

router = APIRouter(tags=["health"])


def get_search_service() -> SearchService:
    raise RuntimeError("Search service dependency is not configured.")


@router.get("/health", response_model=HealthResponse)
async def health(settings: Settings = Depends(get_settings)) -> HealthResponse:
    return HealthResponse(status="healthy", search_provider=settings.search_provider)


@router.get("/health/search", response_model=SearchHealthResponse)
async def search_health(
    settings: Settings = Depends(get_settings),
    search_service: SearchService = Depends(get_search_service),
) -> SearchHealthResponse:
    await search_service.ping()
    return SearchHealthResponse(status="healthy", search_provider=settings.search_provider)
