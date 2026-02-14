"""
ReOrder AI — Pydantic Models
Request/response schemas for all API endpoints.
Strict input validation on all create/update schemas.
"""

import re
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ── Enums ────────────────────────────────────────────────────

class InventoryStatus(str, Enum):
    OK = "OK"
    LOW_STOCK = "LOW_STOCK"
    REORDER_NOW = "REORDER_NOW"
    DEAD_STOCK = "DEAD_STOCK"
    OUT_OF_STOCK = "OUT_OF_STOCK"


class AlertSeverity(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AlertType(str, Enum):
    STOCKOUT_RISK = "Stockout Risk"
    LEAD_TIME_ALERT = "Lead Time Alert"
    DEAD_STOCK = "Dead Stock"
    RESOLUTION = "Resolution"
    PRICE_CHANGE = "Price Change"


class Platform(str, Enum):
    SHOPIFY = "shopify"
    WOOCOMMERCE = "woocommerce"
    MANUAL = "manual"


# ── Inventory Models ─────────────────────────────────────────

class InventoryItem(BaseModel):
    """A single product's inventory record (read-only response)."""
    id: str = Field(description="Internal unique ID")
    sku: str = Field(description="Stock Keeping Unit")
    product_name: str
    platform: Platform = Platform.MANUAL
    current_stock: int = Field(ge=0)
    unit_cost: float = Field(ge=0, default=0.0)
    retail_price: float = Field(ge=0, default=0.0)
    predicted_demand_30d: Optional[float] = None
    reorder_point: Optional[int] = None
    lead_time_days: int = Field(ge=0, default=7)
    safety_stock: int = Field(ge=0, default=0)
    status: InventoryStatus = InventoryStatus.OK
    category: str = Field(default="Uncategorized")
    last_sold_at: Optional[datetime] = None
    last_synced_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class InventoryCreate(BaseModel):
    """Schema for adding a new inventory item. Strict validation."""
    sku: str = Field(min_length=1, max_length=128, description="SKU identifier")
    product_name: str = Field(min_length=1, max_length=256, description="Product name")
    platform: Platform = Platform.MANUAL
    current_stock: int = Field(ge=0, le=10_000_000, default=0)
    unit_cost: float = Field(ge=0, le=1_000_000, default=0.0)
    retail_price: float = Field(ge=0, le=1_000_000, default=0.0)
    lead_time_days: int = Field(ge=0, le=365, default=7)
    safety_stock: int = Field(ge=0, le=1_000_000, default=0)
    category: str = Field(default="Uncategorized", max_length=128)

    @field_validator("sku")
    @classmethod
    def sku_no_whitespace(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("SKU cannot be empty")
        if re.search(r"\s", v):
            raise ValueError("SKU must not contain whitespace")
        return v

    @field_validator("product_name")
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Product name cannot be blank")
        return v


class InventoryUpdate(BaseModel):
    """Schema for updating an existing inventory item (partial update)."""
    product_name: Optional[str] = Field(None, max_length=256)
    current_stock: Optional[int] = Field(None, ge=0, le=10_000_000)
    unit_cost: Optional[float] = Field(None, ge=0, le=1_000_000)
    retail_price: Optional[float] = Field(None, ge=0, le=1_000_000)
    lead_time_days: Optional[int] = Field(None, ge=0, le=365)
    safety_stock: Optional[int] = Field(None, ge=0, le=1_000_000)
    category: Optional[str] = Field(None, max_length=128)
    status: Optional[InventoryStatus] = None


# ── Alert Models ─────────────────────────────────────────────

class Alert(BaseModel):
    """A risk or informational alert."""
    id: str
    type: AlertType
    title: str
    message: str
    severity: AlertSeverity
    sku: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved: bool = False


# ── Dashboard / KPI Models ───────────────────────────────────

class KPI(BaseModel):
    """A single KPI metric for the dashboard."""
    label: str
    value: str
    trend: str
    status: str  # "up", "down", "neutral", "info"


class DashboardResponse(BaseModel):
    """Full dashboard payload for the frontend."""
    kpis: List[KPI]
    alerts: List[Alert]
    health_score: int = Field(ge=0, le=100)
    recommended_action: Optional["RecommendedAction"] = None
    total_items: int = 0
    total_inventory_value: float = 0.0


class RecommendedAction(BaseModel):
    """AI-driven recommended purchase action."""
    skus_count: int
    total_value: str
    message: str
    items: List["ReorderSuggestion"] = []


class ReorderSuggestion(BaseModel):
    """A single SKU reorder suggestion."""
    sku: str
    product_name: str
    current_stock: int
    predicted_demand_30d: float
    suggested_order_qty: int
    estimated_cost: float
    days_until_stockout: int


# ── Dashboard Sub-Endpoint Models ────────────────────────────

class KPIsResponse(BaseModel):
    """Response for /dashboard/kpis."""
    kpis: List[KPI]
    health_score: int = Field(ge=0, le=100)
    total_items: int = 0
    total_inventory_value: float = 0.0


class AlertsResponse(BaseModel):
    """Response for /dashboard/alerts."""
    alerts: List[Alert]
    total_unresolved: int = 0
    total_resolved: int = 0


class TrendDataPoint(BaseModel):
    """A single data point in a time-series trend."""
    label: str = Field(description="e.g. 'Week 1', 'Jan', 'Mon'")
    actual: float = Field(description="Actual stock level or sales")
    projected: float = Field(description="AI-projected value")
    category: str = Field(default="All", description="Product category")


class TrendsResponse(BaseModel):
    """Response for /dashboard/trends."""
    period: str = Field(description="'weekly' or 'monthly'")
    data: List[TrendDataPoint]
    categories: List[str] = Field(description="Available category filters")
    summary: dict = Field(default_factory=dict, description="Trend summary stats")


# ── Sync Models ──────────────────────────────────────────────

class SyncRequest(BaseModel):
    """Request to sync inventory from an external platform."""
    platform: Platform
    full_sync: bool = Field(default=False, description="If True, re-sync all data. If False, incremental.")


class SyncWithCredentialsRequest(BaseModel):
    """Sync using provided store credentials (from Connect flow)."""
    platform: Platform
    full_sync: bool = Field(default=False)
    shop_domain: Optional[str] = Field(None, max_length=256, description="Shopify shop domain")
    access_token: Optional[str] = Field(None, max_length=512, description="Shopify Admin API access token")
    wc_site_url: Optional[str] = Field(None, max_length=512, description="WooCommerce store URL")
    wc_consumer_key: Optional[str] = Field(None, max_length=256, description="WooCommerce consumer key")
    wc_consumer_secret: Optional[str] = Field(None, max_length=256, description="WooCommerce consumer secret")

    @field_validator("shop_domain")
    @classmethod
    def validate_shop_domain(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip().lower()
        if v and not re.match(r"^[a-z0-9][a-z0-9\-]*\.myshopify\.com$", v):
            raise ValueError("shop_domain must be like your-store.myshopify.com")
        return v

    @field_validator("wc_site_url")
    @classmethod
    def validate_wc_url(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if v and not v.startswith(("http://", "https://")):
            raise ValueError("wc_site_url must start with http:// or https://")
        return v.rstrip("/")


class SyncResponse(BaseModel):
    """Response after a sync operation."""
    sync_id: str
    platform: Platform
    status: str  # "initiated", "in_progress", "completed", "failed"
    items_synced: int = 0
    message: str = ""


# ── Pipeline ────────────────────────────────────────────────

class PipelineStoreConfigRequest(BaseModel):
    """Request to set pipeline config for a store."""
    store_id: str = Field(min_length=1, max_length=64)
    platform: str = Field(min_length=1, max_length=32)
    timezone: str = Field(default="UTC", max_length=64)
    base_currency: str = Field(default="USD", min_length=3, max_length=3)

    @field_validator("base_currency")
    @classmethod
    def currency_uppercase(cls, v: str) -> str:
        return v.upper()


class RawOrderRow(BaseModel):
    """Single raw order line for pipeline ingestion."""
    store_id: str = Field(min_length=1, max_length=64)
    external_order_id: str = Field(min_length=1, max_length=128)
    external_line_id: Optional[str] = Field(None, max_length=128)
    sku_raw: str = Field(min_length=1, max_length=128)
    product_id: Optional[str] = Field(None, max_length=128)
    variant_id: Optional[str] = Field(None, max_length=128)
    quantity: int = Field(ge=0, le=10_000_000)
    unit_price: float = Field(ge=0, le=1_000_000)
    currency: str = Field(min_length=3, max_length=3)
    order_date_utc: str = Field(max_length=32)  # ISO datetime
    category: Optional[str] = Field(None, max_length=128)

    @field_validator("order_date_utc")
    @classmethod
    def validate_iso_date(cls, v: str) -> str:
        try:
            from datetime import datetime as dt
            dt.fromisoformat(v.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            raise ValueError("order_date_utc must be a valid ISO 8601 datetime")
        return v


class IngestOrdersRequest(BaseModel):
    """Request to ingest raw orders into the pipeline."""
    orders: List[RawOrderRow] = Field(max_length=10_000, description="Max 10,000 orders per batch")


# ── Forecast Models ──────────────────────────────────────────

class ForecastResultResponse(BaseModel):
    """A single SKU forecast result."""
    sku: str
    store_id: str
    forecast_date: str
    horizon_days: int = 30
    predicted_demand: float
    predicted_revenue: Optional[float] = None
    confidence_low: Optional[float] = None
    confidence_high: Optional[float] = None
    provider: str = "simple"
    days_of_history: Optional[int] = None
    created_at: Optional[datetime] = None


class ForecastRunResponse(BaseModel):
    """Response after running forecasts for a store."""
    store_id: str
    skus_forecasted: int = 0
    skus_skipped: int = 0
    provider: str = "simple"
    errors: List[str] = []


class ForecastListResponse(BaseModel):
    """Response for listing all forecasts for a store."""
    store_id: str
    forecasts: List[ForecastResultResponse] = []
    total: int = 0


# ── Health Check ─────────────────────────────────────────────

class HealthCheck(BaseModel):
    """API health check response."""
    status: str = "healthy"
    version: str = "1.0.0"
    uptime_seconds: float = 0.0
    integrations: dict = {}


# Rebuild forward references
DashboardResponse.model_rebuild()
RecommendedAction.model_rebuild()
