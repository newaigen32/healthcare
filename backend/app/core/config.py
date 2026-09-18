from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "development"
    log_level: str = "INFO"
    search_mode: Literal["mock", "azure"] = "mock"
    cors_origins: str = "http://localhost:3000"

    azure_search_endpoint: str = ""
    azure_search_index_name: str = ""
    azure_search_api_key: str = ""
    azure_search_timeout_seconds: float = 15.0
    azure_search_top: int = Field(default=5, ge=1, le=50)

    azure_search_id_field: str = "id"
    azure_search_title_field: str = "title"
    azure_search_content_field: str = "content"
    azure_search_source_field: str = "source"
    azure_search_category_field: str = "category"

    azure_search_vector_field: str = ""
    azure_search_vector_k: int = Field(default=5, ge=1, le=50)
    azure_search_semantic_configuration: str = ""

    @field_validator("azure_search_endpoint", "azure_search_index_name", "azure_search_api_key", mode="before")
    @classmethod
    def strip_optional(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def hybrid_search_enabled(self) -> bool:
        return bool(self.azure_search_vector_field)

    def validate_for_startup(self) -> None:
        if self.search_mode != "azure":
            return

        missing: list[str] = []
        if not self.azure_search_endpoint:
            missing.append("AZURE_SEARCH_ENDPOINT")
        if not self.azure_search_index_name:
            missing.append("AZURE_SEARCH_INDEX_NAME")
        if not self.azure_search_api_key:
            missing.append("AZURE_SEARCH_API_KEY")
        if missing:
            raise RuntimeError(
                "SEARCH_MODE=azure requires these environment variables: "
                + ", ".join(missing)
            )


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.validate_for_startup()
    return settings
