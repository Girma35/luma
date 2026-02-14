"""
ReOrder AI — Abstract forecast provider interface.
All providers implement this contract so the runner doesn't care which backend is used.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional

import pandas as pd


@dataclass
class ForecastResult:
    """Output of a single SKU forecast."""
    sku: str
    store_id: str
    forecast_date: date
    horizon_days: int
    predicted_demand: float          # total units over horizon
    predicted_revenue: Optional[float] = None
    confidence_low: Optional[float] = None
    confidence_high: Optional[float] = None
    provider: str = "simple"
    days_of_history: int = 0


@dataclass
class ForecastRunSummary:
    """Summary returned after forecasting all SKUs for a store."""
    store_id: str
    skus_forecasted: int = 0
    skus_skipped: int = 0
    provider: str = "simple"
    errors: List[str] = field(default_factory=list)


class ForecastProvider(ABC):
    """
    Abstract base for all forecast backends.
    Each provider receives a pandas DataFrame of daily time-series
    and returns a ForecastResult.
    """

    name: str = "base"

    @abstractmethod
    def predict(
        self,
        store_id: str,
        sku: str,
        history: pd.DataFrame,
        horizon_days: int = 30,
    ) -> ForecastResult:
        """
        Generate a demand forecast for one SKU.

        Args:
            store_id:     The store identifier.
            sku:          The SKU to forecast.
            history:      DataFrame with columns ['series_date', 'quantity', 'revenue'].
                          Sorted by date ascending. One row per day.
            horizon_days: How many days ahead to forecast (default 30).

        Returns:
            ForecastResult with predicted demand and optional confidence interval.
        """
        ...

    def min_history_days(self) -> int:
        """Minimum days of history needed for this provider."""
        return 14
