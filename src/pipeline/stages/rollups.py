"""
Variant rollups: aggregate order lines to daily time-series per (store, SKU, category).
"""

import logging
from datetime import date

import pandas as pd

logger = logging.getLogger(__name__)


class VariantRollup:
    """
    Aggregates order lines to one row per (store_id, sku_id, category_id, series_date)
    with sum(quantity) and sum(revenue). Uses canonical_sku as sku_id.
    """

    def transform(self, orders: pd.DataFrame) -> pd.DataFrame:
        if orders.empty:
            return pd.DataFrame(
                columns=[
                    "store_id", "sku_id", "category_id", "series_date",
                    "quantity", "revenue", "is_interpolated", "is_outlier_adjusted",
                ]
            )
        required = ["store_id", "canonical_sku", "series_date", "quantity", "revenue_base"]
        for c in required:
            if c not in orders.columns:
                raise ValueError(f"orders must have column {c}")
        cat_col = orders["category"].fillna("").astype(str) if "category" in orders.columns else pd.Series("", index=orders.index)
        agg = (
            orders.groupby(
                [
                    orders["store_id"],
                    orders["canonical_sku"].rename("sku_id"),
                    cat_col.rename("category_id"),
                    orders["series_date"],
                ],
                dropna=False,
            )
            .agg(
                quantity=("quantity", "sum"),
                revenue=("revenue_base", "sum"),
            )
            .reset_index()
        )
        agg["is_interpolated"] = False
        agg["is_outlier_adjusted"] = False
        agg["category_id"] = agg["category_id"].replace("", None)
        return agg
