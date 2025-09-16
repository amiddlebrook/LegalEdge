"""Application configuration via environment variables."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the LegalEdge backend."""

    app_name: str = "LegalEdge Platform"
    api_v1_prefix: str = "/api/v1"
    environment: str = "development"
    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/legaledge"
    )
    sync_database_url: str = (
        "postgresql+psycopg://postgres:postgres@localhost:5432/legaledge"
    )
    redis_url: str = "redis://localhost:6379/0"
    ingestion_schedule_minutes: int = 30
    openai_api_key: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="LEGALEDGE_",
        validate_default=False,
        extra="ignore",
    )


settings = Settings()