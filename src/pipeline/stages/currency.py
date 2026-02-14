"""
Currency normalization: convert all amounts to base currency using exchange rates.
"""

import logging

import pandas as pd

from src.pipeline.config import PipelineConfig

logger = logging.getLogger(__name__)


class CurrencyNormalizer:
    """Converts unit_price and computes revenue in base currency."""

    def __init__(self, config: PipelineConfig):
        self.config = config

    def transform(self, orders: pd.DataFrame) -> pd.DataFrame:
        if orders.empty:
            orders["revenue_base"] = pd.Series(dtype=float)
            return orders
        if "unit_price" not in orders.columns or "quantity" not in orders.columns or "currency" not in orders.columns:
            raise ValueError("orders must have unit_price, quantity, currency")
        # Line revenue in original currency
        orders["revenue_base"] = (
            orders["quantity"].astype(float) * orders["unit_price"].astype(float)
        )
        # Convert to base currency
        orders["revenue_base"] = orders.apply(
            lambda row: self.config.to_base_currency(row["revenue_base"], row["currency"]),
            axis=1,
        )
        return orders
