from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.core.config import Settings, get_settings
from app.core.exceptions import SearchServiceError
from app.db.database import ping_database
from app.schemas.search import DatabaseHealthResponse, HealthResponse, SearchHealthResponse
from app.services.search_service import SearchService

router = APIRouter(tags=["health"])


def get_search_service() -> SearchService:
    raise RuntimeError("Search service dependency is not configured.")


@router.get("/health", response_model=HealthResponse)
async def health(settings: Settings = Depends(get_settings)) -> HealthResponse:
    return HealthResponse(status="healthy", search_provider=settings.search_provider)


@router.get("/health/search", response_model=SearchHealthResponse, response_model_exclude_none=True)
async def search_health(
    settings: Settings = Depends(get_settings),
    search_service: SearchService = Depends(get_search_service),
) -> SearchHealthResponse | JSONResponse:
    payload: dict[str, object] = {
        "status": "healthy",
        "provider": settings.search_provider,
        "connected": True,
    }
    if settings.search_provider == "azure":
        payload["index"] = settings.azure_search_index_name

    try:
        await search_service.ping()
    except SearchServiceError:
        payload["status"] = "unavailable"
        payload["connected"] = False
        return JSONResponse(status_code=503, content=payload)

    return SearchHealthResponse.model_validate(payload)


@router.get("/health/database", response_model=DatabaseHealthResponse)
async def database_health() -> DatabaseHealthResponse | JSONResponse:
    try:
        ping_database()
    except Exception:
        return JSONResponse(
            status_code=503,
            content={"status": "unavailable", "connected": False},
        )
    return DatabaseHealthResponse(status="healthy", connected=True)
