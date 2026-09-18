from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health, search
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.services.search_service import SearchService


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(settings)
    search_service = SearchService(settings)
    app.state.search_service = search_service
    yield
    await search_service.close()


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title="Knowledge Assistant API",
        version="1.0.0",
        description="Version 1 search API for company documents indexed in Azure AI Search.",
        lifespan=lifespan,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    def get_search_service() -> SearchService:
        return application.state.search_service

    application.dependency_overrides[search.get_search_service] = get_search_service
    application.include_router(health.router)
    application.include_router(search.router)
    return application


app = create_app()
