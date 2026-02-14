"""
ReOrder AI — Application Configuration
Loads all settings from .env using pydantic-settings for type safety and validation.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Central configuration loaded from .env file."""

    # ── Shopify ──────────────────────────────────────────────
    shopify_shop_url: str = Field(default="", description="e.g. your-shop.myshopify.com")
    shopify_access_token: str = Field(default="", description="Shopify Admin API access token")

    # ── WooCommerce ──────────────────────────────────────────
    woocommerce_site_url: str = Field(default="", description="e.g. https://your-store.com")
    woocommerce_consumer_key: str = Field(default="", description="WooCommerce REST API consumer key")
    woocommerce_consumer_secret: str = Field(default="", description="WooCommerce REST API consumer secret")

    # ── AI Forecasting ───────────────────────────────────────
    forecast_provider: str = Field(default="simple", description="simple | amazon_forecast | google_vertex_ai")
    aws_region: str = Field(default="us-east-1")
    aws_access_key_id: str = Field(default="")
    aws_secret_access_key: str = Field(default="")

    # ── API Settings ─────────────────────────────────────────
    log_level: str = Field(default="INFO")
    port: int = Field(default=8000)
    cors_origins: str = Field(
        default="http://localhost:4321,http://localhost:3000",
        description="Comma-separated list of allowed CORS origins"
    )

    # ── Database ─────────────────────────────────────────────
    database_url: str = Field(
        default="sqlite:///./reorder_ai.db",
        description="SQLite connection string (default) or PostgreSQL URL for production"
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }

    @property
    def cors_origin_list(self) -> list[str]:
        """Parse comma-separated CORS origins into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def shopify_configured(self) -> bool:
        return bool(self.shopify_shop_url and self.shopify_access_token
                     and not self.shopify_access_token.startswith("shpat_xxx"))

    @property
    def woocommerce_configured(self) -> bool:
        return bool(self.woocommerce_site_url and self.woocommerce_consumer_key
                     and not self.woocommerce_consumer_key.startswith("ck_xxx"))


@lru_cache()
def get_settings() -> Settings:
    """
    Cached singleton — call this from anywhere to access config.
    Usage:  from src.core.config import get_settings
            settings = get_settings()
    """
    return Settings()
