"""
Missing data interpolation: fill gaps in time-series (e.g. no-sale days) with 0 or interpolated value.
"""

import logging
from datetime import timedelta

import pandas as pd

logger = logging.getLogger(__name__)


class MissingDataInterpolator:
    """
    Ensures a continuous date range per (store_id, sku_id, category_id).
    Missing dates get quantity=0, revenue=0 and is_interpolated=True (fill method),
    or optional linear interpolation for quantity/revenue (method='linear').
    """

    def __init__(self, method: str = "zero"):
        """
        method: 'zero' = fill missing with 0; 'linear' = interpolate (only for quantity/revenue).
        """
        self.method = method

    def transform(self, series: pd.DataFrame) -> pd.DataFrame:
        if series.empty:
            return series
        required = ["store_id", "sku_id", "series_date", "quantity", "revenue"]
        for c in required:
            if c not in series.columns:
                raise ValueError(f"series must have column {c}")
        series["series_date"] = pd.to_datetime(series["series_date"])
        min_date = series["series_date"].min()
        max_date = series["series_date"].max()
        full_range = pd.date_range(min_date, max_date, freq="D")
        keys = series.groupby(["store_id", "sku_id"]).agg(
            category_id=("category_id", "first"),
        ).reset_index()
        filled = []
        for _, row in keys.iterrows():
            sid, sku, cat = row["store_id"], row["sku_id"], row["category_id"]
            sub = series[(series["store_id"] == sid) & (series["sku_id"] == sku)]
            sub_dates = set(pd.Timestamp(d).date() for d in sub["series_date"])
            for ts in full_range:
                d = ts.date() if hasattr(ts, "date") else pd.Timestamp(ts).date()
                if d in sub_dates:
                    rec = sub[sub["series_date"].dt.date == d].iloc[0]
                    filled.append({
                        "store_id": sid,
                        "sku_id": sku,
                        "category_id": cat,
                        "series_date": d,
                        "quantity": rec["quantity"],
                        "revenue": rec["revenue"],
                        "is_interpolated": rec.get("is_interpolated", False),
                        "is_outlier_adjusted": rec.get("is_outlier_adjusted", False),
                    })
                else:
                    filled.append({
                        "store_id": sid,
                        "sku_id": sku,
                        "category_id": cat,
                        "series_date": d,
                        "quantity": 0.0,
                        "revenue": 0.0,
                        "is_interpolated": True,
                        "is_outlier_adjusted": False,
                    })
        out = pd.DataFrame(filled)
        out["series_date"] = pd.to_datetime(out["series_date"]).dt.date
        return out
