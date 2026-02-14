"""
ReOrder AI — FastAPI Application
Hardened: /api/v1 versioning, rate limiting, API key auth, production CORS.
"""

import logging
import time
from typing import Optional, List

from fastapi import FastAPI, APIRouter, HTTPException, Query, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from sqlalchemy.orm import Session

from src.core.config import get_settings
from src.core import store as inventory_store
from src.db.session import init_db, get_db
from src.api.deps import get_client_ip, require_api_key
from src.api.models import (
    InventoryItem, InventoryCreate, InventoryUpdate, InventoryStatus,
    Alert, DashboardResponse, SyncRequest, SyncResponse, SyncWithCredentialsRequest,
    HealthCheck, Platform, KPIsResponse, AlertsResponse, TrendsResponse,
    PipelineStoreConfigRequest, IngestOrdersRequest, RawOrderRow,
    ForecastRunResponse, ForecastListResponse, ForecastResultResponse,
)

logger = logging.getLogger(__name__)

# ── Settings ─────────────────────────────────────────────────

settings = get_settings()
START_TIME = time.time()

# ── Rate Limiter ─────────────────────────────────────────────

limiter = Limiter(key_func=get_client_ip, default_limits=[settings.rate_limit_default])

# ── App ──────────────────────────────────────────────────────

app = FastAPI(
    title="ReOrder AI API",
    description="Supply chain forecasting and inventory optimization for Shopify and WooCommerce",
    version="1.0.0",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json",
)

app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": f"Rate limit exceeded: {exc.detail}"},
    )


# ── CORS ─────────────────────────────────────────────────────
# In production: only configured domains. In dev: also allow localhost.

cors_origins = settings.cors_origin_list

if settings.is_production:
    # Production: strict — only what's in CORS_ORIGINS
    allow_methods = ["GET", "POST", "PATCH", "DELETE", "OPTIONS"]
    allow_headers = ["Content-Type", "Authorization", "X-API-Key"]
else:
    # Development: more permissive
    allow_methods = ["*"]
    allow_headers = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=allow_methods,
    allow_headers=allow_headers,
)


# ── Lifecycle ────────────────────────────────────────────────

@app.on_event("startup")
def startup():
    """Create all DB tables and start background scheduler on startup."""
    init_db()
    from src.jobs.scheduler import start_scheduler
    if settings.forecast_refresh_hours > 0:
        start_scheduler()
    logger.info(
        "ReOrder AI started | env=%s | cors=%s | auth=%s | rate_limit=%s",
        settings.environment,
        cors_origins,
        "enabled" if settings.api_secret_key else "disabled (dev)",
        settings.rate_limit_default,
    )


@app.on_event("shutdown")
def shutdown():
    from src.jobs.scheduler import stop_scheduler
    stop_scheduler()


# ── Root (unversioned) ───────────────────────────────────────

@app.get("/", tags=["Health"])
async def root():
    return {
        "message": "ReOrder AI API",
        "version": "1.0.0",
        "docs": "/api/v1/docs",
        "health": "/api/v1/health",
    }


# ══════════════════════════════════════════════════════════════
#  /api/v1 — All versioned endpoints
# ══════════════════════════════════════════════════════════════

v1 = APIRouter(prefix="/api/v1")


# ── Health ───────────────────────────────────────────────────

@v1.get("/health", response_model=HealthCheck, tags=["Health"])
async def health_check():
    return HealthCheck(
        status="healthy",
        version="1.0.0",
        uptime_seconds=round(time.time() - START_TIME, 1),
        integrations={
            "shopify": "user-provided",
            "woocommerce": "user-provided",
            "forecasting": settings.forecast_provider,
        },
    )


# ── Dashboard ────────────────────────────────────────────────

@v1.get("/dashboard", response_model=DashboardResponse, tags=["Dashboard"])
@limiter.limit(settings.rate_limit_default)
def get_dashboard(request: Request, db: Session = Depends(get_db)):
    """Full dashboard payload: KPIs, alerts, health score, recommended actions."""
    return inventory_store.get_dashboard(db)


@v1.get("/dashboard/kpis", response_model=KPIsResponse, tags=["Dashboard"])
@limiter.limit(settings.rate_limit_default)
def get_dashboard_kpis(request: Request, db: Session = Depends(get_db)):
    """KPI metrics and health score."""
    return inventory_store.get_kpis(db)


@v1.get("/dashboard/alerts", response_model=AlertsResponse, tags=["Dashboard"])
@limiter.limit(settings.rate_limit_default)
def get_dashboard_alerts(request: Request, db: Session = Depends(get_db)):
    """All alerts with unresolved/resolved counts."""
    return inventory_store.get_alerts_summary(db)


@v1.get("/dashboard/trends", response_model=TrendsResponse, tags=["Dashboard"])
@limiter.limit(settings.rate_limit_default)
def get_dashboard_trends(
    request: Request,
    period: str = Query("weekly", description="'weekly' or 'monthly'"),
    category: Optional[str] = Query(None, description="Filter by product category"),
    db: Session = Depends(get_db),
):
    """Time-series trend data for the Inventory Trends chart."""
    if period not in ("weekly", "monthly"):
        raise HTTPException(status_code=400, detail="Period must be 'weekly' or 'monthly'")
    return inventory_store.get_trends(db, period=period, category=category)


# ── Inventory CRUD ───────────────────────────────────────────

@v1.get("/inventory", response_model=List[InventoryItem], tags=["Inventory"])
@limiter.limit(settings.rate_limit_default)
def list_inventory(
    request: Request,
    status: Optional[InventoryStatus] = Query(None),
    platform: Optional[Platform] = Query(None),
    category: Optional[str] = Query(None, max_length=128),
    search: Optional[str] = Query(None, max_length=256),
    db: Session = Depends(get_db),
):
    """List inventory items with optional filters."""
    return inventory_store.list_items(db, status=status, platform=platform, category=category, search=search)


@v1.get("/inventory/{item_id}", response_model=InventoryItem, tags=["Inventory"])
@limiter.limit(settings.rate_limit_default)
def get_inventory_item(request: Request, item_id: str, db: Session = Depends(get_db)):
    item = inventory_store.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    return item


@v1.get("/inventory/sku/{sku}", response_model=InventoryItem, tags=["Inventory"])
@limiter.limit(settings.rate_limit_default)
def get_inventory_item_by_sku(request: Request, sku: str, db: Session = Depends(get_db)):
    item = inventory_store.get_item_by_sku(db, sku)
    if not item:
        raise HTTPException(status_code=404, detail=f"SKU {sku} not found")
    return item


@v1.post("/inventory", response_model=InventoryItem, status_code=201, tags=["Inventory"])
@limiter.limit(settings.rate_limit_default)
def create_inventory_item(
    request: Request, data: InventoryCreate, db: Session = Depends(get_db),
    _key: str = Depends(require_api_key),
):
    existing = inventory_store.get_item_by_sku(db, data.sku)
    if existing:
        raise HTTPException(status_code=409, detail=f"SKU {data.sku} already exists")
    return inventory_store.add_item(db, data)


@v1.patch("/inventory/{item_id}", response_model=InventoryItem, tags=["Inventory"])
@limiter.limit(settings.rate_limit_default)
def update_inventory_item(
    request: Request, item_id: str, data: InventoryUpdate,
    db: Session = Depends(get_db), _key: str = Depends(require_api_key),
):
    updated = inventory_store.update_item(db, item_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    return updated


@v1.delete("/inventory/{item_id}", tags=["Inventory"])
@limiter.limit(settings.rate_limit_default)
def delete_inventory_item(
    request: Request, item_id: str,
    db: Session = Depends(get_db), _key: str = Depends(require_api_key),
):
    if not inventory_store.delete_item(db, item_id):
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    return {"message": f"Item {item_id} deleted"}


# ── Alerts ───────────────────────────────────────────────────

@v1.get("/alerts", response_model=List[Alert], tags=["Alerts"])
@limiter.limit(settings.rate_limit_default)
def list_alerts_endpoint(
    request: Request,
    include_resolved: bool = Query(False),
    db: Session = Depends(get_db),
):
    return inventory_store.list_alerts(db, include_resolved=include_resolved)


# ── Sync (auth + stricter rate limit) ────────────────────────

@v1.post("/sync", response_model=SyncResponse, tags=["Sync"])
@limiter.limit(settings.rate_limit_sync)
async def sync_inventory(
    request: Request, data: SyncRequest, _key: str = Depends(require_api_key),
):
    """Initiate a sync with an external platform. Requires API key.
    Note: Store credentials are provided by users via /sync/with-credentials."""
    import uuid

    return SyncResponse(
        sync_id=f"sync_{uuid.uuid4().hex[:8]}",
        platform=data.platform,
        status="initiated",
        items_synced=0,
        message=f"{data.platform.value} sync initiated. Full sync: {data.full_sync}. Use /sync/with-credentials for credential-based sync.",
    )


@v1.post("/sync/with-credentials", response_model=SyncResponse, tags=["Sync"])
@limiter.limit(settings.rate_limit_sync)
async def sync_with_credentials(
    request: Request, data: SyncWithCredentialsRequest, _key: str = Depends(require_api_key),
):
    """Sync using credentials from the Connect flow. Requires API key."""
    import uuid

    if data.platform == Platform.SHOPIFY:
        if not data.shop_domain or not data.access_token:
            raise HTTPException(status_code=400, detail="Shopify requires shop_domain and access_token")
        return SyncResponse(
            sync_id=f"sync_{uuid.uuid4().hex[:8]}",
            platform=Platform.SHOPIFY, status="initiated", items_synced=0,
            message=f"Shopify sync initiated for {data.shop_domain}.",
        )
    if data.platform == Platform.WOOCOMMERCE:
        if not data.wc_site_url or not data.wc_consumer_key or not data.wc_consumer_secret:
            raise HTTPException(status_code=400, detail="WooCommerce requires wc_site_url, wc_consumer_key, wc_consumer_secret")
        return SyncResponse(
            sync_id=f"sync_{uuid.uuid4().hex[:8]}",
            platform=Platform.WOOCOMMERCE, status="initiated", items_synced=0,
            message=f"WooCommerce sync initiated for {data.wc_site_url}.",
        )
    raise HTTPException(status_code=400, detail="Unsupported platform")


# ── Forecast (auth + stricter rate limit on run) ─────────────

@v1.post("/forecast/{store_id}/run", response_model=ForecastRunResponse, tags=["Forecast"])
@limiter.limit(settings.rate_limit_sync)
def run_forecast(
    request: Request, store_id: str,
    horizon_days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db), _key: str = Depends(require_api_key),
):
    """Run demand forecasts for all SKUs in a store. Requires API key."""
    from src.core.forecast import get_provider
    from src.core.forecast.runner import run_forecasts

    provider = get_provider()
    summary = run_forecasts(db, store_id, provider, horizon_days)
    return ForecastRunResponse(
        store_id=summary.store_id,
        skus_forecasted=summary.skus_forecasted,
        skus_skipped=summary.skus_skipped,
        provider=summary.provider,
        errors=summary.errors,
    )


@v1.get("/forecast/{store_id}", response_model=ForecastListResponse, tags=["Forecast"])
@limiter.limit(settings.rate_limit_default)
def list_forecasts(request: Request, store_id: str, db: Session = Depends(get_db)):
    """Get the latest forecast for every SKU in a store."""
    from src.db.models import ForecastResultDB
    from sqlalchemy import func

    latest = (
        db.query(ForecastResultDB.sku, func.max(ForecastResultDB.created_at).label("max_created"))
        .filter(ForecastResultDB.store_id == store_id)
        .group_by(ForecastResultDB.sku)
        .subquery()
    )
    rows = (
        db.query(ForecastResultDB)
        .join(latest, (ForecastResultDB.sku == latest.c.sku) & (ForecastResultDB.created_at == latest.c.max_created))
        .filter(ForecastResultDB.store_id == store_id)
        .order_by(ForecastResultDB.sku)
        .all()
    )
    forecasts = [
        ForecastResultResponse(
            sku=r.sku, store_id=r.store_id, forecast_date=r.forecast_date.isoformat(),
            horizon_days=r.horizon_days, predicted_demand=r.predicted_demand,
            predicted_revenue=r.predicted_revenue, confidence_low=r.confidence_low,
            confidence_high=r.confidence_high, provider=r.provider,
            days_of_history=r.days_of_history, created_at=r.created_at,
        ) for r in rows
    ]
    return ForecastListResponse(store_id=store_id, forecasts=forecasts, total=len(forecasts))


@v1.get("/forecast/{store_id}/{sku}", response_model=ForecastResultResponse, tags=["Forecast"])
@limiter.limit(settings.rate_limit_default)
def get_forecast_for_sku(request: Request, store_id: str, sku: str, db: Session = Depends(get_db)):
    from src.db.models import ForecastResultDB
    row = (
        db.query(ForecastResultDB)
        .filter(ForecastResultDB.store_id == store_id, ForecastResultDB.sku == sku)
        .order_by(ForecastResultDB.created_at.desc()).first()
    )
    if not row:
        raise HTTPException(status_code=404, detail=f"No forecast for {sku} in store {store_id}")
    return ForecastResultResponse(
        sku=row.sku, store_id=row.store_id, forecast_date=row.forecast_date.isoformat(),
        horizon_days=row.horizon_days, predicted_demand=row.predicted_demand,
        predicted_revenue=row.predicted_revenue, confidence_low=row.confidence_low,
        confidence_high=row.confidence_high, provider=row.provider,
        days_of_history=row.days_of_history, created_at=row.created_at,
    )


# ── Pipeline (auth + stricter rate limit) ────────────────────

@v1.post("/pipeline/{store_id}/run", tags=["Pipeline"])
@limiter.limit(settings.rate_limit_sync)
async def run_pipeline(
    request: Request, store_id: str,
    outlier_strategy: str = Query("cap", description="cap | flag | none"),
    interpolation_method: str = Query("zero", description="zero | linear"),
    _key: str = Depends(require_api_key),
):
    """Run the data normalization pipeline. Requires API key."""
    if outlier_strategy not in ("cap", "flag", "none"):
        raise HTTPException(status_code=400, detail="outlier_strategy must be cap, flag, or none")
    if interpolation_method not in ("zero", "linear"):
        raise HTTPException(status_code=400, detail="interpolation_method must be zero or linear")

    from src.pipeline.runner import PipelineRunner
    try:
        runner = PipelineRunner(store_id=store_id, outlier_strategy=outlier_strategy, interpolation_method=interpolation_method)
        return runner.run()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@v1.get("/pipeline/{store_id}/series", tags=["Pipeline"])
@limiter.limit(settings.rate_limit_default)
def get_normalized_series(
    request: Request, store_id: str,
    sku_id: Optional[str] = Query(None, max_length=128),
    category_id: Optional[str] = Query(None, max_length=128),
    from_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    to_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    db: Session = Depends(get_db),
):
    from src.db.models import NormalizedSeries
    q = db.query(NormalizedSeries).filter(NormalizedSeries.store_id == store_id)
    if sku_id:
        q = q.filter(NormalizedSeries.sku_id == sku_id)
    if category_id:
        q = q.filter(NormalizedSeries.category_id == category_id)
    if from_date:
        q = q.filter(NormalizedSeries.series_date >= from_date)
    if to_date:
        q = q.filter(NormalizedSeries.series_date <= to_date)
    rows = q.order_by(NormalizedSeries.series_date).all()
    return [
        {
            "store_id": r.store_id, "sku_id": r.sku_id, "category_id": r.category_id,
            "series_date": r.series_date.isoformat() if r.series_date else None,
            "quantity": r.quantity, "revenue": r.revenue,
            "is_interpolated": r.is_interpolated, "is_outlier_adjusted": r.is_outlier_adjusted,
        }
        for r in rows
    ]


@v1.post("/pipeline/ingest/orders", tags=["Pipeline"])
@limiter.limit(settings.rate_limit_sync)
def ingest_raw_orders(
    request: Request, body: IngestOrdersRequest,
    db: Session = Depends(get_db), _key: str = Depends(require_api_key),
):
    """Ingest raw order lines. Requires API key."""
    from datetime import datetime as dt
    from src.db.models import RawOrder
    if not body.orders:
        return {"ingested": 0}
    for row in body.orders:
        db.add(RawOrder(
            store_id=row.store_id, external_order_id=row.external_order_id,
            external_line_id=row.external_line_id, sku_raw=row.sku_raw,
            product_id=row.product_id, variant_id=row.variant_id,
            quantity=row.quantity, unit_price=row.unit_price, currency=row.currency,
            order_date_utc=dt.fromisoformat(row.order_date_utc.replace("Z", "+00:00")),
            category=row.category,
        ))
    return {"ingested": len(body.orders)}


@v1.post("/pipeline/store-config", tags=["Pipeline"])
@limiter.limit(settings.rate_limit_sync)
async def set_pipeline_store_config(
    request: Request, body: PipelineStoreConfigRequest, _key: str = Depends(require_api_key),
):
    """Create or update pipeline config. Requires API key."""
    from src.pipeline.config import ensure_store_config
    ensure_store_config(body.store_id, body.platform, timezone=body.timezone, base_currency=body.base_currency)
    return {"store_id": body.store_id, "timezone": body.timezone, "base_currency": body.base_currency}


# ── Mount versioned router ───────────────────────────────────

app.include_router(v1)
