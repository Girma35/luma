"""
ReOrder AI — SQLAlchemy models.
Pipeline tables + Inventory / Alert tables.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    String,
    Integer,
    Float,
    DateTime,
    Date,
    Boolean,
    ForeignKey,
    Text,
    Index,
    Enum as SAEnum,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Declarative base for all models."""
    pass


# ── Pipeline Tables ───────────────────────────────────────────


class PipelineStoreConfig(Base):
    """Per-store pipeline configuration: timezone and base currency."""
    __tablename__ = "pipeline_store_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    store_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    platform: Mapped[str] = mapped_column(String(32), nullable=False)
    timezone: Mapped[str] = mapped_column(String(64), nullable=False, default="UTC")
    base_currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class RawOrder(Base):
    """Raw order line items from store APIs (pre-normalization)."""
    __tablename__ = "raw_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    store_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    external_order_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    external_line_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    sku_raw: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    product_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    variant_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    order_date_utc: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    category: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (Index("ix_raw_orders_store_date", "store_id", "order_date_utc"),)


class RawRefund(Base):
    """Raw refunds to adjust revenue (linked to order)."""
    __tablename__ = "raw_refunds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    store_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    external_order_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    refund_date_utc: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class RawProduct(Base):
    """Raw product/variant catalog for SKU and category context."""
    __tablename__ = "raw_products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    store_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    sku_raw: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    product_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    variant_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (Index("ix_raw_products_store_sku", "store_id", "sku_raw", unique=True),)


class SKUMapping(Base):
    """Maps raw SKU/variant IDs to canonical SKU for deduplication."""
    __tablename__ = "sku_mappings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    store_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    sku_raw: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    canonical_sku: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (Index("ix_sku_mappings_store_raw", "store_id", "sku_raw", unique=True),)


class NormalizedSeries(Base):
    """
    Output of the pipeline: clean time-series per SKU / category / store.
    One row per (store, sku, category, date).
    """
    __tablename__ = "normalized_series"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    store_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    sku_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    category_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)
    series_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    quantity: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    revenue: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    is_interpolated: Mapped[bool] = mapped_column(Boolean, default=False)
    is_outlier_adjusted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_normalized_series_store_sku_date", "store_id", "sku_id", "series_date", unique=True),
        Index("ix_normalized_series_store_date", "store_id", "series_date"),
    )


# ── Inventory Tables ──────────────────────────────────────────


class InventoryItemDB(Base):
    """Persisted inventory item (replaces in-memory InventoryStore)."""
    __tablename__ = "inventory_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    public_id: Mapped[str] = mapped_column(String(16), unique=True, nullable=False, index=True)
    sku: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    product_name: Mapped[str] = mapped_column(String(256), nullable=False)
    platform: Mapped[str] = mapped_column(String(32), nullable=False, default="manual")
    current_stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    unit_cost: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    retail_price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    predicted_demand_30d: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    reorder_point: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    lead_time_days: Mapped[int] = mapped_column(Integer, nullable=False, default=7)
    safety_stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="OK")
    category: Mapped[str] = mapped_column(String(128), nullable=False, default="Uncategorized")
    store_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    last_sold_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_inventory_items_store_sku", "store_id", "sku"),
        Index("ix_inventory_items_status", "status"),
    )


class AlertDB(Base):
    """Persisted alert record."""
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    public_id: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(16), nullable=False, default="medium")
    sku: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)
    store_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    resolved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_alerts_store_resolved", "store_id", "resolved"),
    )


class ForecastResultDB(Base):
    """Persisted per-SKU demand forecast results."""
    __tablename__ = "forecast_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    store_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    sku: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    forecast_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    horizon_days: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    predicted_demand: Mapped[float] = mapped_column(Float, nullable=False)
    predicted_revenue: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    confidence_low: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    confidence_high: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    provider: Mapped[str] = mapped_column(String(64), nullable=False, default="simple")
    days_of_history: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_forecast_results_store_sku_date", "store_id", "sku", "forecast_date"),
        Index("ix_forecast_results_latest", "store_id", "sku", "created_at"),
    )


class ReorderRuleDB(Base):
    """Per-SKU reorder rules (thresholds, auto-reorder settings)."""
    __tablename__ = "reorder_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    store_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    sku: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    reorder_point: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    reorder_qty: Mapped[int] = mapped_column(Integer, nullable=False, default=50)
    auto_reorder: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    supplier_email: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_reorder_rules_store_sku", "store_id", "sku", unique=True),
    )
