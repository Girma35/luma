"""
Timezone normalization: ensure all order timestamps are in UTC and series_date is date-only.
"""

import logging
from datetime import datetime

import pandas as pd

from src.pipeline.schemas import ORDER_DF_COLS

logger = logging.getLogger(__name__)


class TimezoneNormalizer:
    """
    Ensures order_date_utc is timezone-aware UTC and extracts date for grouping.
    If ingestion already stores UTC, this is a no-op except for adding series_date.
    """

    def __init__(self, store_timezone: str = "UTC"):
        self.store_timezone = store_timezone

    def transform(self, orders: pd.DataFrame) -> pd.DataFrame:
        if orders.empty:
            orders["series_date"] = pd.Series(dtype="datetime64[ns]")
            return orders
        if "order_date_utc" not in orders.columns:
            raise ValueError("orders must have column order_date_utc")
        # Ensure datetime and normalize to UTC (if we had tz-aware we'd convert here)
        orders["order_date_utc"] = pd.to_datetime(orders["order_date_utc"], utc=True)
        orders["series_date"] = orders["order_date_utc"].dt.date
        return orders
