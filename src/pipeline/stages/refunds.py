"""
Refund adjustments: subtract refund amounts from order revenue before rollup.
Applied at order level so each order line gets a share of refund (or full refund to first line).
"""

import logging
from typing import Optional

import pandas as pd
from sqlalchemy.orm import Session

from src.db.models import RawRefund
from src.pipeline.config import PipelineConfig

logger = logging.getLogger(__name__)


class RefundAdjustment:
    """
    Loads refunds for the store, converts to base currency, and subtracts from
    order revenue. We assign refund to order by external_order_id and reduce
    revenue_base proportionally (or subtract from first line).
    """

    def __init__(self, session: Session, config: PipelineConfig):
        self.session = session
        self.config = config

    def transform(self, orders: pd.DataFrame) -> pd.DataFrame:
        if orders.empty:
            return orders
        if "revenue_base" not in orders.columns or "external_order_id" not in orders.columns:
            raise ValueError("orders must have revenue_base and external_order_id")
        store_id = orders["store_id"].iloc[0]
        refunds = (
            self.session.query(RawRefund)
            .filter(RawRefund.store_id == store_id)
            .all()
        )
        if not refunds:
            return orders
        # Build order_id -> total refund in base currency
        refund_by_order = {}
        for r in refunds:
            amount_base = self.config.to_base_currency(r.amount, r.currency)
            refund_by_order[r.external_order_id] = refund_by_order.get(r.external_order_id, 0.0) + amount_base
        # Per order: total line revenue; then assign refund proportionally
        orders["_order_revenue"] = orders.groupby("external_order_id")["revenue_base"].transform("sum")
        orders["_refund"] = orders["external_order_id"].map(refund_by_order).fillna(0.0)
        # Reduce revenue_base by refund share (proportional to line revenue)
        orders["_refund_share"] = orders.apply(
            lambda row: (row["revenue_base"] / row["_order_revenue"] * row["_refund"])
            if row["_order_revenue"] and row["_order_revenue"] > 0
            else 0.0,
            axis=1,
        )
        orders["revenue_base"] = (orders["revenue_base"] - orders["_refund_share"]).clip(lower=0.0)
        orders.drop(columns=["_order_revenue", "_refund", "_refund_share"], inplace=True)
        return orders
