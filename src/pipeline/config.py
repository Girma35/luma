"""
ReOrder AI — Pipeline configuration (per-store timezone and currency).
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.db.session import get_session
from src.db.models import PipelineStoreConfig


@dataclass
class PipelineConfig:
    """Runtime config for a pipeline run (timezone, base currency, exchange rates)."""
    store_id: str
    timezone: str
    base_currency: str
    exchange_rates: dict[str, float]  # currency code -> rate to base_currency

    def to_base_currency(self, amount: float, currency: str) -> float:
        """Convert amount from given currency to base currency."""
        if currency == self.base_currency:
            return amount
        rate = self.exchange_rates.get(currency.upper())
        if rate is None:
            return amount  # fallback: assume 1:1 if missing
        return amount * rate


def get_store_pipeline_config(store_id: str) -> Optional[PipelineConfig]:
    """Load pipeline config for a store from DB. Returns None if not found."""
    with get_session() as session:
        row = (
            session.query(PipelineStoreConfig)
            .filter(PipelineStoreConfig.store_id == store_id)
            .first()
        )
        if not row:
            return None
        # Stub: single-currency or static rates; in production use an FX API
        rates = {row.base_currency: 1.0}
        return PipelineConfig(
            store_id=row.store_id,
            timezone=row.timezone or "UTC",
            base_currency=row.base_currency or "USD",
            exchange_rates=rates,
        )


def ensure_store_config(store_id: str, platform: str, timezone: str = "UTC", base_currency: str = "USD") -> None:
    """Create or update pipeline config for a store."""
    with get_session() as session:
        row = (
            session.query(PipelineStoreConfig)
            .filter(PipelineStoreConfig.store_id == store_id)
            .first()
        )
        if row:
            row.timezone = timezone
            row.base_currency = base_currency
            row.updated_at = datetime.utcnow()
        else:
            session.add(
                PipelineStoreConfig(
                    store_id=store_id,
                    platform=platform,
                    timezone=timezone,
                    base_currency=base_currency,
                )
            )
