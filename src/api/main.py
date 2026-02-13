from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(
    title="ReOrder AI API",
    description="Supply chain forecasting and inventory optimization for Shopify and WooCommerce",
    version="1.0.0"
)

class InventoryItem(BaseModel):
    sku: str
    product_name: str
    current_stock: int
    predicted_demand_30d: Optional[float] = None
    reorder_point: Optional[int] = None
    status: str  # e.g., "OK", "REORDER_NOW", "DEAD_STOCK"

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

@app.get("/inventory", response_model=List[InventoryItem])
async def get_inventory():
    # Placeholder for actual data retrieval
    return [
        {
            "sku": "SAMPLE-001",
            "product_name": "Premium Cotton Tee",
            "current_stock": 15,
            "predicted_demand_30d": 45.5,
            "reorder_point": 20,
            "status": "REORDER_NOW"
        },
        {
            "sku": "SAMPLE-002",
            "product_name": "Organic Denim Jacket",
            "current_stock": 120,
            "predicted_demand_30d": 12.0,
            "reorder_point": 10,
            "status": "DEAD_STOCK"
        }
    ]

@app.post("/sync/shopify")
async def sync_shopify():
    # Placeholder for Shopify API sync
    return {"message": "Shopify sync initiated", "sync_id": "sh_12345"}

@app.post("/sync/woocommerce")
async def sync_woocommerce():
    # Placeholder for WooCommerce API sync
    return {"message": "WooCommerce sync initiated", "sync_id": "wc_67890"}
