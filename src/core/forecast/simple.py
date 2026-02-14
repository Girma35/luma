"""
ReOrder AI — Simple local forecast provider.
Uses exponential smoothing (Holt-Winters) when statsmodels is available,
otherwise falls back to weighted moving average. Zero external dependencies required.
"""

import logging
from datetime import date
from typing import Optional

import numpy as np
import pandas as pd

from src.core.forecast.base import ForecastProvider, ForecastResult

logger = logging.getLogger(__name__)


class SimpleProvider(ForecastProvider):
    """
    Lightweight local forecaster.
    - >= 14 days history with weekly seasonality → Holt-Winters (statsmodels)
    - < 14 days or statsmodels unavailable → weighted moving average
    """

    name = "simple"

    def predict(
        self,
        store_id: str,
        sku: str,
        history: pd.DataFrame,
        horizon_days: int = 30,
    ) -> ForecastResult:
        days = len(history)
        if days == 0:
            return self._empty_result(store_id, sku, horizon_days, days)

        # Try Holt-Winters if we have enough data
        if days >= 14:
            try:
                return self._holt_winters(store_id, sku, history, horizon_days)
            except Exception as e:
                logger.warning("Holt-Winters failed for %s/%s: %s — falling back to WMA", store_id, sku, e)

        return self._weighted_moving_average(store_id, sku, history, horizon_days)

    def min_history_days(self) -> int:
        return 7  # WMA fallback works with as few as 7 days

    # ── Holt-Winters (primary) ────────────────────────────────

    def _holt_winters(
        self, store_id: str, sku: str, history: pd.DataFrame, horizon_days: int
    ) -> ForecastResult:
        from statsmodels.tsa.holtwinters import ExponentialSmoothing

        series = history.set_index("series_date")["quantity"].asfreq("D", fill_value=0)

        # Seasonal period = 7 (weekly) if we have at least 2 full weeks
        seasonal_periods = 7 if len(series) >= 14 else None
        seasonal = "add" if seasonal_periods else None

        model = ExponentialSmoothing(
            series,
            trend="add",
            seasonal=seasonal,
            seasonal_periods=seasonal_periods,
            initialization_method="estimated",
        ).fit(optimized=True)

        forecast = model.forecast(horizon_days)
        predicted_demand = max(0.0, float(forecast.sum()))

        # Confidence via residual std dev (approximate 80% interval)
        residuals = model.resid
        std = float(residuals.std()) if len(residuals) > 1 else 0.0
        total_std = std * np.sqrt(horizon_days)
        confidence_low = max(0.0, predicted_demand - 1.28 * total_std)
        confidence_high = predicted_demand + 1.28 * total_std

        # Revenue estimate: avg revenue per unit * predicted demand
        avg_rev_per_unit = (
            history["revenue"].sum() / history["quantity"].sum()
            if history["quantity"].sum() > 0 else 0.0
        )

        return ForecastResult(
            sku=sku,
            store_id=store_id,
            forecast_date=date.today(),
            horizon_days=horizon_days,
            predicted_demand=round(predicted_demand, 1),
            predicted_revenue=round(predicted_demand * avg_rev_per_unit, 2),
            confidence_low=round(confidence_low, 1),
            confidence_high=round(confidence_high, 1),
            provider="simple/holt_winters",
            days_of_history=len(history),
        )

    # ── Weighted Moving Average (fallback) ────────────────────

    def _weighted_moving_average(
        self, store_id: str, sku: str, history: pd.DataFrame, horizon_days: int
    ) -> ForecastResult:
        quantities = history["quantity"].values
        n = len(quantities)

        # Exponentially decaying weights: recent days matter more
        weights = np.array([2 ** i for i in range(n)], dtype=float)
        weights /= weights.sum()
        daily_avg = float(np.dot(weights, quantities))

        predicted_demand = max(0.0, daily_avg * horizon_days)

        # Simple confidence: +/- 1 std dev of daily quantities
        std = float(np.std(quantities)) if n > 1 else daily_avg * 0.3
        total_std = std * np.sqrt(horizon_days)
        confidence_low = max(0.0, predicted_demand - total_std)
        confidence_high = predicted_demand + total_std

        avg_rev_per_unit = (
            history["revenue"].sum() / history["quantity"].sum()
            if history["quantity"].sum() > 0 else 0.0
        )

        return ForecastResult(
            sku=sku,
            store_id=store_id,
            forecast_date=date.today(),
            horizon_days=horizon_days,
            predicted_demand=round(predicted_demand, 1),
            predicted_revenue=round(predicted_demand * avg_rev_per_unit, 2),
            confidence_low=round(confidence_low, 1),
            confidence_high=round(confidence_high, 1),
            provider="simple/wma",
            days_of_history=n,
        )

    # ── Empty result ──────────────────────────────────────────

    def _empty_result(
        self, store_id: str, sku: str, horizon_days: int, days: int
    ) -> ForecastResult:
        return ForecastResult(
            sku=sku,
            store_id=store_id,
            forecast_date=date.today(),
            horizon_days=horizon_days,
            predicted_demand=0.0,
            predicted_revenue=0.0,
            confidence_low=0.0,
            confidence_high=0.0,
            provider="simple/no_data",
            days_of_history=days,
        )
