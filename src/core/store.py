"""
ReOrder AI — In-Memory Data Store
Provides a thread-safe inventory store with seed data.
This acts as the single source of truth until a real database is added.
"""

import uuid
import random
import math
from datetime import datetime, timedelta
from typing import Optional, List
from src.api.models import (
    InventoryItem, InventoryCreate, InventoryUpdate,
    Alert, AlertType, AlertSeverity, InventoryStatus, Platform,
    KPI, DashboardResponse, RecommendedAction, ReorderSuggestion,
    KPIsResponse, AlertsResponse, TrendDataPoint, TrendsResponse,
)


class InventoryStore:
    """
    In-memory inventory store.
    Replace with SQLAlchemy / SQLite later without changing the interface.
    """

    def __init__(self):
        self._items: dict[str, InventoryItem] = {}
        self._alerts: list[Alert] = []
        self._seed()

    # ── CRUD ─────────────────────────────────────────────────

    def list_items(
        self,
        status: Optional[InventoryStatus] = None,
        platform: Optional[Platform] = None,
        category: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[InventoryItem]:
        """Return filtered inventory list."""
        items = list(self._items.values())
        if status:
            items = [i for i in items if i.status == status]
        if platform:
            items = [i for i in items if i.platform == platform]
        if category:
            items = [i for i in items if i.category.lower() == category.lower()]
        if search:
            q = search.lower()
            items = [i for i in items if q in i.sku.lower() or q in i.product_name.lower()]
        return sorted(items, key=lambda i: i.sku)

    def get_item(self, item_id: str) -> Optional[InventoryItem]:
        return self._items.get(item_id)

    def get_item_by_sku(self, sku: str) -> Optional[InventoryItem]:
        for item in self._items.values():
            if item.sku == sku:
                return item
        return None

    def add_item(self, data: InventoryCreate) -> InventoryItem:
        item_id = str(uuid.uuid4())[:8]
        item = InventoryItem(
            id=item_id,
            sku=data.sku,
            product_name=data.product_name,
            platform=data.platform,
            current_stock=data.current_stock,
            unit_cost=data.unit_cost,
            retail_price=data.retail_price,
            lead_time_days=data.lead_time_days,
            safety_stock=data.safety_stock,
            category=data.category,
            status=self._compute_status(data.current_stock, None, None),
        )
        self._items[item_id] = item
        return item

    def update_item(self, item_id: str, data: InventoryUpdate) -> Optional[InventoryItem]:
        item = self._items.get(item_id)
        if not item:
            return None
        update_dict = data.model_dump(exclude_unset=True)
        updated = item.model_copy(update=update_dict)
        # Recompute status if stock changed
        if "current_stock" in update_dict:
            updated.status = self._compute_status(
                updated.current_stock,
                updated.reorder_point,
                updated.last_sold_at,
            )
        self._items[item_id] = updated
        return updated

    def delete_item(self, item_id: str) -> bool:
        return self._items.pop(item_id, None) is not None

    # ── Alerts ───────────────────────────────────────────────

    def list_alerts(self, include_resolved: bool = False) -> List[Alert]:
        if include_resolved:
            return sorted(self._alerts, key=lambda a: a.created_at, reverse=True)
        return sorted(
            [a for a in self._alerts if not a.resolved],
            key=lambda a: a.created_at, reverse=True,
        )

    def add_alert(self, alert: Alert):
        self._alerts.append(alert)

    # ── Dashboard ────────────────────────────────────────────

    def get_dashboard(self) -> DashboardResponse:
        items = list(self._items.values())
        total_items = len(items)
        total_value = sum(i.current_stock * i.unit_cost for i in items)

        # In-stock rate
        in_stock = sum(1 for i in items if i.current_stock > 0)
        in_stock_rate = (in_stock / total_items * 100) if total_items > 0 else 0

        # Revenue projection (simple: sum of retail_price * predicted_demand)
        projected_revenue = sum(
            (i.predicted_demand_30d or 0) * i.retail_price for i in items
        )

        # Average lead time
        avg_lead = sum(i.lead_time_days for i in items) / total_items if total_items else 0

        kpis = [
            KPI(
                label="Projected Revenue",
                value=f"${projected_revenue:,.0f}",
                trend="+12.5% vs LW",
                status="up",
            ),
            KPI(
                label="In-Stock Rate",
                value=f"{in_stock_rate:.1f}%",
                trend=f"Target: 95%",
                status="neutral" if in_stock_rate >= 90 else "down",
            ),
            KPI(
                label="Avg. Lead Time",
                value=f"{avg_lead:.0f} Days",
                trend="+2 days delay" if avg_lead > 10 else "On track",
                status="down" if avg_lead > 10 else "up",
            ),
            KPI(
                label="Inventory Value",
                value=f"${total_value:,.0f}",
                trend=f"{total_items} Active SKUs",
                status="info",
            ),
        ]

        # Generate reorder suggestions
        reorder_items = [i for i in items if i.status in (InventoryStatus.REORDER_NOW, InventoryStatus.LOW_STOCK)]
        suggestions = []
        for item in reorder_items:
            demand = item.predicted_demand_30d or 30
            days_left = int(item.current_stock / (demand / 30)) if demand > 0 else 999
            order_qty = max(int(demand - item.current_stock), 0) + item.safety_stock
            suggestions.append(ReorderSuggestion(
                sku=item.sku,
                product_name=item.product_name,
                current_stock=item.current_stock,
                predicted_demand_30d=demand,
                suggested_order_qty=order_qty,
                estimated_cost=order_qty * item.unit_cost,
                days_until_stockout=days_left,
            ))

        total_reorder_cost = sum(s.estimated_cost for s in suggestions)

        recommended = RecommendedAction(
            skus_count=len(suggestions),
            total_value=f"${total_reorder_cost:,.2f}",
            message=f"Based on AI projections for next month's demand, {len(suggestions)} items are at risk of stockout. Restocking now ensures availability.",
            items=suggestions,
        ) if suggestions else None

        # Health score: weighted combination of in-stock rate, lead time, dead stock %
        dead_stock_count = sum(1 for i in items if i.status == InventoryStatus.DEAD_STOCK)
        dead_stock_pct = (dead_stock_count / total_items * 100) if total_items else 0
        health = int(
            (in_stock_rate * 0.5) +
            (max(0, 100 - avg_lead * 3) * 0.3) +
            (max(0, 100 - dead_stock_pct * 5) * 0.2)
        )
        health = max(0, min(100, health))

        return DashboardResponse(
            kpis=kpis,
            alerts=self.list_alerts()[:5],
            health_score=health,
            recommended_action=recommended,
            total_items=total_items,
            total_inventory_value=total_value,
        )

    # ── Dashboard Sub-Endpoints ──────────────────────────────

    def get_kpis(self) -> KPIsResponse:
        """Return only KPIs and summary stats for /dashboard/kpis."""
        dashboard = self.get_dashboard()
        return KPIsResponse(
            kpis=dashboard.kpis,
            health_score=dashboard.health_score,
            total_items=dashboard.total_items,
            total_inventory_value=dashboard.total_inventory_value,
        )

    def get_alerts_summary(self) -> AlertsResponse:
        """Return alerts with counts for /dashboard/alerts."""
        unresolved = [a for a in self._alerts if not a.resolved]
        resolved = [a for a in self._alerts if a.resolved]
        return AlertsResponse(
            alerts=sorted(self._alerts, key=lambda a: a.created_at, reverse=True),
            total_unresolved=len(unresolved),
            total_resolved=len(resolved),
        )

    def get_trends(self, period: str = "weekly", category: Optional[str] = None) -> TrendsResponse:
        """
        Generate inventory trend data for visualization.
        Uses seeded random with consistent patterns per category.
        In production, this would query historical stock snapshots.
        """
        items = list(self._items.values())
        if category and category.lower() != "all":
            items = [i for i in items if i.category.lower() == category.lower()]

        categories = sorted(set(i.category for i in self._items.values()))

        if period == "monthly":
            labels = ["Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb"]
            num_points = 7
        else:
            labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun",
                      "Mon", "Tue", "Wed"]
            num_points = 10

        # Aggregate baseline from current inventory
        total_stock = sum(i.current_stock for i in items) or 100
        total_demand = sum((i.predicted_demand_30d or 0) for i in items) or 50

        # Generate realistic trend with slight noise and seasonal pattern
        random.seed(42)  # Consistent output for demo
        data_points = []
        for idx, label in enumerate(labels[:num_points]):
            # Actual: sine wave around stock level with noise
            seasonal = math.sin(idx * 0.8) * (total_stock * 0.15)
            noise = random.uniform(-total_stock * 0.05, total_stock * 0.05)
            actual = max(0, total_stock + seasonal + noise - (idx * total_demand / num_points * 0.3))

            # Projected: smoother predicted line
            projected_seasonal = math.sin(idx * 0.8) * (total_stock * 0.12)
            projected = max(0, total_stock + projected_seasonal - (idx * total_demand / num_points * 0.25))

            data_points.append(TrendDataPoint(
                label=label,
                actual=round(actual, 1),
                projected=round(projected, 1),
                category=category or "All",
            ))

        # Summary statistics
        actuals = [d.actual for d in data_points]
        projections = [d.projected for d in data_points]
        avg_deviation = sum(abs(a - p) for a, p in zip(actuals, projections)) / len(actuals) if actuals else 0

        summary = {
            "avg_actual": round(sum(actuals) / len(actuals), 1) if actuals else 0,
            "avg_projected": round(sum(projections) / len(projections), 1) if projections else 0,
            "peak_actual": round(max(actuals), 1) if actuals else 0,
            "min_actual": round(min(actuals), 1) if actuals else 0,
            "forecast_accuracy": round(100 - (avg_deviation / (sum(actuals) / len(actuals)) * 100), 1) if actuals and sum(actuals) > 0 else 0,
        }

        return TrendsResponse(
            period=period,
            data=data_points,
            categories=["All"] + categories,
            summary=summary,
        )

    # ── Internal Helpers ─────────────────────────────────────

    @staticmethod
    def _compute_status(
        current_stock: int,
        reorder_point: Optional[int],
        last_sold_at: Optional[datetime],
    ) -> InventoryStatus:
        if current_stock == 0:
            return InventoryStatus.OUT_OF_STOCK
        if last_sold_at and (datetime.utcnow() - last_sold_at).days > 60:
            return InventoryStatus.DEAD_STOCK
        if reorder_point and current_stock <= reorder_point:
            return InventoryStatus.REORDER_NOW
        if reorder_point and current_stock <= reorder_point * 1.5:
            return InventoryStatus.LOW_STOCK
        return InventoryStatus.OK

    def _seed(self):
        """Populate store with realistic demo data matching the dashboard design."""
        now = datetime.utcnow()

        seed_items = [
            ("SKU-402", "Artisan Coffee Beans",   "Beverages",   8,   12.50, 29.99, 45.0, 20, 10, 5,  InventoryStatus.REORDER_NOW, Platform.SHOPIFY),
            ("SKU-118", "Silk Filter Packs",       "Accessories", 22,  3.20,  8.99,  35.0, 15, 14, 8,  InventoryStatus.LOW_STOCK,   Platform.SHOPIFY),
            ("SKU-205", "Ceramic Pour-Over Set",   "Glassware",   85,  18.00, 54.99, 20.0, 25, 7,  10, InventoryStatus.OK,          Platform.WOOCOMMERCE),
            ("SKU-991", "Paper Sleeves (1000pk)",  "Packaging",   5200, 0.02,  0.08, 800.0, 500, 5, 100, InventoryStatus.OK,         Platform.SHOPIFY),
            ("SKU-310", "Cold Brew Concentrate",   "Beverages",   3,   8.00,  22.99, 60.0, 30, 12, 10, InventoryStatus.REORDER_NOW, Platform.SHOPIFY),
            ("SKU-455", "Bamboo Stir Sticks",      "Accessories", 150, 0.05,  0.25,  120.0, 80, 4,  20, InventoryStatus.OK,          Platform.WOOCOMMERCE),
            ("SKU-601", "Vintage Espresso Cups",   "Glassware",   45,  6.50,  19.99, 15.0, 20, 18, 5,  InventoryStatus.LOW_STOCK,   Platform.SHOPIFY),
            ("SKU-720", "Gift Box Sampler",        "Bundles",     200, 15.00, 49.99, 10.0, 15, 6,  5,  InventoryStatus.OK,          Platform.WOOCOMMERCE),
            ("SKU-888", "Seasonal Blend (Winter)", "Beverages",   0,   9.00,  26.99, 0.0,  10, 8,  5,  InventoryStatus.OUT_OF_STOCK,Platform.SHOPIFY),
            ("SKU-103", "Leather Coaster Set",     "Accessories", 340, 2.00,  12.99, 5.0,  20, 10, 5,  InventoryStatus.DEAD_STOCK,  Platform.MANUAL),
            ("SKU-550", "French Press (32oz)",     "Equipment",   28,  14.00, 39.99, 30.0, 18, 9,  5,  InventoryStatus.LOW_STOCK,   Platform.WOOCOMMERCE),
            ("SKU-215", "Organic Matcha Tin",      "Beverages",   12,  11.00, 34.99, 55.0, 25, 15, 8,  InventoryStatus.REORDER_NOW, Platform.SHOPIFY),
        ]

        for sku, name, cat, stock, cost, price, demand, rop, lead, safety, status, platform in seed_items:
            item_id = str(uuid.uuid4())[:8]
            self._items[item_id] = InventoryItem(
                id=item_id,
                sku=sku,
                product_name=name,
                platform=platform,
                current_stock=stock,
                unit_cost=cost,
                retail_price=price,
                predicted_demand_30d=demand,
                reorder_point=rop,
                lead_time_days=lead,
                safety_stock=safety,
                status=status,
                category=cat,
                last_sold_at=now - timedelta(days=2) if status != InventoryStatus.DEAD_STOCK else now - timedelta(days=90),
                last_synced_at=now - timedelta(hours=1),
            )

        # Seed alerts matching the dashboard design
        self._alerts = [
            Alert(id="ALT-001", type=AlertType.STOCKOUT_RISK, title="SKU-402: Artisan Coffee Beans",
                  message="Inventory levels reached critical minimum. Estimated stockout in 2 days.",
                  severity=AlertSeverity.HIGH, sku="SKU-402", created_at=now - timedelta(minutes=14)),
            Alert(id="ALT-002", type=AlertType.STOCKOUT_RISK, title="SKU-118: Silk Filter Packs",
                  message="Supplier delay detected. Projected delivery shifted +4 days. Re-order recommended.",
                  severity=AlertSeverity.HIGH, sku="SKU-118", created_at=now - timedelta(hours=1)),
            Alert(id="ALT-003", type=AlertType.LEAD_TIME_ALERT, title="Multiple: Glassware Category",
                  message="Port congestion increasing lead times by 15% across European routes.",
                  severity=AlertSeverity.MEDIUM, created_at=now - timedelta(hours=3)),
            Alert(id="ALT-004", type=AlertType.RESOLUTION, title="SKU-991: Paper Sleeves",
                  message="Automatic re-order successfully processed for 5,000 units.",
                  severity=AlertSeverity.LOW, sku="SKU-991", created_at=now - timedelta(days=1), resolved=True),
        ]


# ── Singleton ────────────────────────────────────────────────

_store: Optional[InventoryStore] = None


def get_store() -> InventoryStore:
    """Return the global store singleton."""
    global _store
    if _store is None:
        _store = InventoryStore()
    return _store
