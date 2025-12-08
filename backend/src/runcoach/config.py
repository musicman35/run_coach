"""Application configuration using pydantic-settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Database
    database_url: str = "postgresql+asyncpg://localhost/runcoach"

    # Anthropic
    anthropic_api_key: str = ""

    # Strava
    strava_client_id: str = ""
    strava_client_secret: str = ""

    # Resend (email)
    resend_api_key: str = ""

    # Application
    secret_key: str = "change-me-in-production"
    debug: bool = False


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
