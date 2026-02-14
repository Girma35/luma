"""
Unit tests for pipeline normalizer stages.
"""

import pandas as pd
import pytest
from datetime import datetime, date

from src.pipeline.stages.timezone import TimezoneNormalizer
from src.pipeline.stages.currency import CurrencyNormalizer
from src.pipeline.stages.rollups import VariantRollup
from src.pipeline.stages.outliers import OutlierDetector
from src.pipeline.config import PipelineConfig


@pytest.fixture
def sample_orders():
    return pd.DataFrame([
        {
            "store_id": "s1",
            "external_order_id": "o1",
            "sku_raw": "SKU-A",
            "quantity": 2,
            "unit_price": 10.0,
            "currency": "USD",
            "order_date_utc": "2024-01-15T12:00:00Z",
            "category": "Beverages",
        },
        {
            "store_id": "s1",
            "external_order_id": "o1",
            "sku_raw": "SKU-B",
            "quantity": 1,
            "unit_price": 25.0,
            "currency": "USD",
            "order_date_utc": "2024-01-15T12:00:00Z",
            "category": "Beverages",
        },
    ])


def test_timezone_normalizer_adds_series_date(sample_orders):
    tz = TimezoneNormalizer(store_timezone="UTC")
    out = tz.transform(sample_orders.copy())
    assert "series_date" in out.columns
    assert out["series_date"].iloc[0] == date(2024, 1, 15)


def test_currency_normalizer_adds_revenue_base(sample_orders):
    config = PipelineConfig("s1", "UTC", "USD", {"USD": 1.0})
    curr = CurrencyNormalizer(config=config)
    sample_orders["series_date"] = date(2024, 1, 15)
    out = curr.transform(sample_orders.copy())
    assert "revenue_base" in out.columns
    assert out["revenue_base"].iloc[0] == 20.0
    assert out["revenue_base"].iloc[1] == 25.0


def test_variant_rollup_aggregates(sample_orders):
    sample_orders["series_date"] = date(2024, 1, 15)
    sample_orders["revenue_base"] = [20.0, 25.0]
    sample_orders["canonical_sku"] = sample_orders["sku_raw"]
    rollup = VariantRollup()
    out = rollup.transform(sample_orders)
    assert len(out) == 2  # two SKUs
    assert set(out["sku_id"]) == {"SKU-A", "SKU-B"}
    assert out[out["sku_id"] == "SKU-A"]["quantity"].iloc[0] == 2
    assert out[out["sku_id"] == "SKU-B"]["revenue"].iloc[0] == 25.0


def test_outlier_detector_caps_extreme():
    series = pd.DataFrame([
        {"store_id": "s1", "sku_id": "SKU-1", "series_date": date(2024, 1, 1), "quantity": 10, "revenue": 100, "is_interpolated": False, "is_outlier_adjusted": False},
        {"store_id": "s1", "sku_id": "SKU-1", "series_date": date(2024, 1, 2), "quantity": 12, "revenue": 120, "is_interpolated": False, "is_outlier_adjusted": False},
        {"store_id": "s1", "sku_id": "SKU-1", "series_date": date(2024, 1, 3), "quantity": 1000, "revenue": 10000, "is_interpolated": False, "is_outlier_adjusted": False},
    ])
    det = OutlierDetector(strategy="cap", iqr_multiplier=1.5)
    out = det.transform(series)
    assert out["is_outlier_adjusted"].any()
    assert out[out["series_date"] == date(2024, 1, 3)]["quantity"].iloc[0] < 1000
