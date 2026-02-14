"""
ReOrder AI — Forecast engine.
Factory that returns the configured provider (simple or aws).
Falls back to simple if AWS credentials are missing or invalid.
"""

import logging
from src.core.config import get_settings
from src.core.forecast.base import ForecastProvider

logger = logging.getLogger(__name__)


def get_provider() -> ForecastProvider:
    """Return the forecast provider configured in settings."""
    settings = get_settings()
    name = settings.forecast_provider.lower().strip()

    if name == "amazon_forecast":
        try:
            from src.core.forecast.aws import AWSForecastProvider
            provider = AWSForecastProvider()
            logger.info("Using AWS Forecast provider")
            return provider
        except Exception as e:
            logger.warning(
                "AWS Forecast provider failed to initialize: %s — falling back to simple", e
            )

    # Default: lightweight local model
    from src.core.forecast.simple import SimpleProvider
    return SimpleProvider()
