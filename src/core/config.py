"""
ReOrder AI — Application Configuration
Loads all settings from .env using pydantic-settings for type safety and validation.

Store credentials (Shopify/WooCommerce) come from users via the dashboard
Connect flow, NOT from .env. Only server-operator settings go here.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Central configuration loaded from .env file."""

    # ── Environment ──────────────────────────────────────────
    environment: str = Field(
        default="development",
        description="development | staging | production"
    )

    # ── Database ─────────────────────────────────────────────
    database_url: str = Field(
        default="sqlite:///./reorder_ai.db",
        description="SQLite (default) or PostgreSQL URL for production"
    )

    # ── API Settings ─────────────────────────────────────────
    log_level: str = Field(default="INFO")
    port: int = Field(default=8000)
    cors_origins: str = Field(
        default="http://localhost:4321,http://localhost:3000",
        description="Comma-separated list of allowed CORS origins"
    )

    # ── Security ─────────────────────────────────────────────
    api_secret_key: str = Field(
        default="",
        description="API key for protected endpoints. Empty = auth disabled (dev mode)."
    )
    rate_limit_default: str = Field(
        default="60/minute",
        description="Default rate limit (e.g. '60/minute', '1000/hour')"
    )
    rate_limit_sync: str = Field(
        default="10/minute",
        description="Stricter rate limit for sync/pipeline/forecast-run endpoints"
    )

    # ── AWS (for Forecast service) ───────────────────────────
    forecast_provider: str = Field(
        default="simple",
        description="simple (local math fallback) | amazon_forecast (AWS)"
    )
    aws_region: str = Field(default="us-east-1")
    aws_access_key_id: str = Field(default="")
    aws_secret_access_key: str = Field(default="")

    # ── Forecast Scheduler ───────────────────────────────────
    forecast_refresh_hours: int = Field(
        default=24,
        description="Auto-refresh forecasts every N hours. 0 = disabled."
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }

    @property
    def is_production(self) -> bool:
        return self.environment.lower() in ("production", "prod")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache()
def get_settings() -> Settings:
    """Cached singleton — call from anywhere to access config."""
    return Settings()
