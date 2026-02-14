from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(
    title="ReOrder AI API",
    description="Supply chain forecasting and inventory optimization for Shopify and WooCommerce",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4321", "http://127.0.0.1:4321"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InventoryItem(BaseModel):
    sku: str
    product_name: str
    current_stock: int
    predicted_demand_30d: Optional[float] = None
    reorder_point: Optional[int] = None
    status: str  # e.g., "OK", "REORDER_NOW", "DEAD_STOCK"

SAMPLE_INVENTORY: List[dict] = [
    {"sku": "SAMPLE-001", "product_name": "Premium Cotton Tee", "current_stock": 15, "predicted_demand_30d": 45.5, "reorder_point": 20, "status": "REORDER_NOW"},
    {"sku": "SAMPLE-002", "product_name": "Organic Denim Jacket", "current_stock": 120, "predicted_demand_30d": 12.0, "reorder_point": 10, "status": "DEAD_STOCK"},
    {"sku": "SAMPLE-003", "product_name": "Minimalist Sneakers", "current_stock": 88, "predicted_demand_30d": 42.0, "reorder_point": 50, "status": "OK"},
    {"sku": "SAMPLE-004", "product_name": "Wool Blend Scarf", "current_stock": 5, "predicted_demand_30d": 28.0, "reorder_point": 15, "status": "REORDER_NOW"},
    {"sku": "SAMPLE-005", "product_name": "Vintage Logo Cap", "current_stock": 200, "predicted_demand_30d": 8.0, "reorder_point": 20, "status": "DEAD_STOCK"},
    {"sku": "SAMPLE-006", "product_name": "Stretch Joggers", "current_stock": 34, "predicted_demand_30d": 38.0, "reorder_point": 30, "status": "OK"},
    {"sku": "SAMPLE-007", "product_name": "Leather Crossbody Bag", "current_stock": 3, "predicted_demand_30d": 18.0, "reorder_point": 12, "status": "REORDER_NOW"},
]

@app.get("/")
async def root():
    return {
        "message": "Welcome to ReOrder AI API",
        "status": "active",
        "features": [
            "Shopify Integration",
            "WooCommerce Integration",
            "Demand Forecasting",
            "Inventory Optimization"
        ]
    }

@app.get("/health")
async def health():
    return {"status": "ok"}

class InsightsSummary(BaseModel):
    reorder_now: int
    dead_stock: int
    healthy: int
    total: int

@app.get("/insights", response_model=InsightsSummary)
async def get_insights():
    inv = SAMPLE_INVENTORY
    reorder_now = sum(1 for i in inv if i["status"] == "REORDER_NOW")
    dead_stock = sum(1 for i in inv if i["status"] == "DEAD_STOCK")
    healthy = sum(1 for i in inv if i["status"] == "OK")
    return {"reorder_now": reorder_now, "dead_stock": dead_stock, "healthy": healthy, "total": len(inv)}

@app.get("/inventory", response_model=List[InventoryItem])
async def get_inventory():
    return [InventoryItem(**item) for item in SAMPLE_INVENTORY]

@app.post("/sync/shopify")
async def sync_shopify():
    # Placeholder for Shopify API sync
    return {"message": "Shopify sync initiated", "sync_id": "sh_12345"}

@app.post("/sync/woocommerce")
async def sync_woocommerce():
    # Placeholder for WooCommerce API sync
    return {"message": "WooCommerce sync initiated", "sync_id": "wc_67890"}
