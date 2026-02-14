"""
ReOrder AI — Pydantic schemas for pipeline data structures.
Used for validation and type-safe interchange between stages.
"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class StorePipelineConfig(BaseModel):
    """Per-store pipeline configuration."""
    store_id: str
    timezone: str = "UTC"
    base_currency: str = "USD"


class RawOrderRecord(BaseModel):
    """Single raw order line (pre-normalization)."""
    store_id: str
    external_order_id: str
    external_line_id: Optional[str] = None
    sku_raw: str
    product_id: Optional[str] = None
    variant_id: Optional[str] = None
    quantity: int
    unit_price: float
    currency: str
    order_date_utc: datetime
    category: Optional[str] = None


class RawRefundRecord(BaseModel):
    """Single raw refund."""
    store_id: str
    external_order_id: str
    amount: float
    currency: str
    refund_date_utc: datetime


class NormalizedRecord(BaseModel):
    """One row of the clean time-series output."""
    store_id: str
    sku_id: str
    category_id: Optional[str] = None
    series_date: date
    quantity: float = 0.0
    revenue: float = 0.0
    is_interpolated: bool = False
    is_outlier_adjusted: bool = False


# Column names used in pipeline DataFrames (internal contract)
ORDER_DF_COLS = [
    "store_id", "external_order_id", "external_line_id", "sku_raw",
    "product_id", "variant_id", "quantity", "unit_price", "currency",
    "order_date_utc", "category",
]
SERIES_DF_COLS = [
    "store_id", "sku_id", "category_id", "series_date",
    "quantity", "revenue", "is_interpolated", "is_outlier_adjusted",
]
