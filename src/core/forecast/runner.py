"""
ReOrder AI — Forecast runner.
Orchestrates: load history → call provider → write results → update inventory.
"""

import logging
from datetime import date
from typing import Dict, List, Optional

import pandas as pd
from sqlalchemy.orm import Session

from src.core.forecast.base import ForecastProvider, ForecastResult, ForecastRunSummary
from src.db.models import NormalizedSeries, InventoryItemDB, ForecastResultDB

logger = logging.getLogger(__name__)


def _load_history(db: Session, store_id: str) -> Dict[str, pd.DataFrame]:
    """
    Load daily time-series from normalized_series, grouped by SKU.
    Returns {sku: DataFrame[series_date, quantity, revenue]}.
    """
    rows = (
        db.query(NormalizedSeries)
        .filter(NormalizedSeries.store_id == store_id)
        .order_by(NormalizedSeries.sku_id, NormalizedSeries.series_date)
        .all()
    )

    sku_data: Dict[str, list] = {}
    for r in rows:
        sku_data.setdefault(r.sku_id, []).append({
            "series_date": r.series_date,
            "quantity": r.quantity,
            "revenue": r.revenue,
        })

    return {
        sku: pd.DataFrame(records) for sku, records in sku_data.items()
    }


def _write_result(db: Session, result: ForecastResult):
    """Persist a single forecast result to the DB."""
    db.add(ForecastResultDB(
        store_id=result.store_id,
        sku=result.sku,
        forecast_date=result.forecast_date,
        horizon_days=result.horizon_days,
        predicted_demand=result.predicted_demand,
        predicted_revenue=result.predicted_revenue,
        confidence_low=result.confidence_low,
        confidence_high=result.confidence_high,
        provider=result.provider,
        days_of_history=result.days_of_history,
    ))


def _update_inventory_demand(db: Session, store_id: str, sku: str, demand: float):
    """Update predicted_demand_30d on the matching inventory item."""
    item = (
        db.query(InventoryItemDB)
        .filter(InventoryItemDB.sku == sku)
        .first()
    )
    if item:
        item.predicted_demand_30d = demand
        logger.debug("Updated predicted_demand_30d for %s → %.1f", sku, demand)


def run_forecasts(
    db: Session,
    store_id: str,
    provider: ForecastProvider,
    horizon_days: int = 30,
) -> ForecastRunSummary:
    """
    Run forecasts for every SKU in a store.

    1. Load normalized time-series from DB
    2. For AWS provider with enough data → bulk predict
       For simple provider → predict per SKU
    3. Write results to forecast_results table
    4. Update predicted_demand_30d on inventory_items
    """
    summary = ForecastRunSummary(
        store_id=store_id,
        provider=provider.name,
    )

    # Load history
    all_history = _load_history(db, store_id)
    if not all_history:
        logger.info("No normalized series data for store %s — nothing to forecast", store_id)
        return summary

    min_days = provider.min_history_days()
    results: List[ForecastResult] = []

    # Check if this is the AWS provider and do bulk prediction
    from src.core.forecast.aws import AWSForecastProvider
    if isinstance(provider, AWSForecastProvider):
        # Split into AWS-eligible (>= 14 days) and fallback
        aws_eligible = {
            sku: df for sku, df in all_history.items() if len(df) >= MIN_HISTORY_AWS
        }
        fallback_skus = {
            sku: df for sku, df in all_history.items() if len(df) < MIN_HISTORY_AWS
        }

        # Bulk predict via AWS
        if aws_eligible:
            try:
                aws_results = provider.predict_bulk(store_id, aws_eligible, horizon_days)
                results.extend(aws_results)
                summary.skus_forecasted += len(aws_results)
            except Exception as e:
                logger.error("AWS Forecast bulk failed: %s — falling back to simple for all", e)
                summary.errors.append(str(e))
                # Fall back: put all eligible back into fallback
                fallback_skus.update(aws_eligible)

        # Fallback for short-history SKUs
        if fallback_skus:
            from src.core.forecast.simple import SimpleProvider
            simple = SimpleProvider()
            for sku, df in fallback_skus.items():
                if len(df) < simple.min_history_days():
                    summary.skus_skipped += 1
                    continue
                try:
                    result = simple.predict(store_id, sku, df, horizon_days)
                    results.append(result)
                    summary.skus_forecasted += 1
                except Exception as e:
                    logger.error("Simple fallback failed for %s: %s", sku, e)
                    summary.errors.append(f"{sku}: {e}")
    else:
        # Simple provider: predict per SKU
        for sku, df in all_history.items():
            if len(df) < min_days:
                summary.skus_skipped += 1
                logger.debug("Skipping %s: only %d days (need %d)", sku, len(df), min_days)
                continue
            try:
                result = provider.predict(store_id, sku, df, horizon_days)
                results.append(result)
                summary.skus_forecasted += 1
            except Exception as e:
                logger.error("Forecast failed for %s: %s", sku, e)
                summary.errors.append(f"{sku}: {e}")

    # Write results and update inventory
    for result in results:
        _write_result(db, result)
        _update_inventory_demand(db, store_id, result.sku, result.predicted_demand)

    db.flush()
    logger.info(
        "Forecast run complete for store %s: %d forecasted, %d skipped, %d errors",
        store_id, summary.skus_forecasted, summary.skus_skipped, len(summary.errors),
    )
    return summary


# AWS minimum history constant
MIN_HISTORY_AWS = 14
