"""
ReOrder AI — Pydantic Models
Request/response schemas for all API endpoints.
"""

from pydantic import BaseModel, Field
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
    """A single product's inventory record."""
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
    """Schema for adding a new inventory item."""
    sku: str
    product_name: str
    platform: Platform = Platform.MANUAL
    current_stock: int = Field(ge=0)
    unit_cost: float = Field(ge=0, default=0.0)
    retail_price: float = Field(ge=0, default=0.0)
    lead_time_days: int = Field(ge=0, default=7)
    safety_stock: int = Field(ge=0, default=0)
    category: str = "Uncategorized"


class InventoryUpdate(BaseModel):
    """Schema for updating an existing inventory item (partial update)."""
    product_name: Optional[str] = None
    current_stock: Optional[int] = None
    unit_cost: Optional[float] = None
    retail_price: Optional[float] = None
    lead_time_days: Optional[int] = None
    safety_stock: Optional[int] = None
    category: Optional[str] = None
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


class SyncResponse(BaseModel):
    """Response after a sync operation."""
    sync_id: str
    platform: Platform
    status: str  # "initiated", "in_progress", "completed", "failed"
    items_synced: int = 0
    message: str = ""


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
