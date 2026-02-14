"""
ReOrder AI — Pipeline orchestrator.
Runs normalizer stages in order and persists clean time-series to DB.
"""

import logging
from datetime import date, datetime
from typing import Optional, Any

import pandas as pd

from src.db.session import get_session
from src.db.models import RawOrder, RawRefund, NormalizedSeries
from src.pipeline.config import PipelineConfig, get_store_pipeline_config
from src.pipeline.stages.timezone import TimezoneNormalizer
from src.pipeline.stages.currency import CurrencyNormalizer
from src.pipeline.stages.refunds import RefundAdjustment
from src.pipeline.stages.dedup import SKUDeduplicator
from src.pipeline.stages.rollups import VariantRollup
from src.pipeline.stages.outliers import OutlierDetector
from src.pipeline.stages.interpolation import MissingDataInterpolator

logger = logging.getLogger(__name__)


class PipelineRunner:
    """
    Runs the full normalization pipeline for a store:
    Load raw orders/refunds -> Timezone -> Currency -> Refund adjustment ->
    SKU dedup -> Variant rollup -> Outlier detection -> Interpolation -> Write.
    """

    def __init__(
        self,
        store_id: str,
        config: Optional[PipelineConfig] = None,
        outlier_strategy: str = "cap",
        interpolation_method: str = "zero",
    ):
        self.store_id = store_id
        self.config = config or get_store_pipeline_config(store_id)
        if not self.config:
            self.config = PipelineConfig(
                store_id=store_id,
                timezone="UTC",
                base_currency="USD",
                exchange_rates={"USD": 1.0},
            )
        self.outlier_strategy = outlier_strategy
        self.interpolation_method = interpolation_method

    def _load_raw_orders(self, session) -> pd.DataFrame:
        rows = (
            session.query(RawOrder)
            .filter(RawOrder.store_id == self.store_id)
            .all()
        )
        if not rows:
            return pd.DataFrame()
        return pd.DataFrame(
            [
                {
                    "store_id": r.store_id,
                    "external_order_id": r.external_order_id,
                    "external_line_id": r.external_line_id,
                    "sku_raw": r.sku_raw,
                    "product_id": r.product_id,
                    "variant_id": r.variant_id,
                    "quantity": r.quantity,
                    "unit_price": r.unit_price,
                    "currency": r.currency,
                    "order_date_utc": r.order_date_utc,
                    "category": r.category,
                }
                for r in rows
            ]
        )

    def run(self) -> dict:
        """
        Execute the pipeline. Returns a summary with row counts and any errors.
        """
        result = {"store_id": self.store_id, "stages": {}, "output_rows": 0, "error": None}
        with get_session() as session:
            try:
                orders = self._load_raw_orders(session)
                result["stages"]["loaded_orders"] = len(orders)
                if orders.empty:
                    logger.warning("No raw orders for store %s", self.store_id)
                    return result

                # 1. Timezone
                tz = TimezoneNormalizer(store_timezone=self.config.timezone)
                orders = tz.transform(orders)
                result["stages"]["after_timezone"] = len(orders)

                # 2. Currency
                curr = CurrencyNormalizer(config=self.config)
                orders = curr.transform(orders)

                # 3. Refund adjustment (before rollup)
                ref = RefundAdjustment(session=session, config=self.config)
                orders = ref.transform(orders)

                # 4. SKU dedup
                dedup = SKUDeduplicator(session=session, store_id=self.store_id)
                orders = dedup.transform(orders)

                # 5. Variant rollup -> series
                rollup = VariantRollup()
                series = rollup.transform(orders)
                result["stages"]["after_rollup"] = len(series)

                # 6. Outliers
                out = OutlierDetector(strategy=self.outlier_strategy)
                series = out.transform(series)

                # 7. Interpolation
                interp = MissingDataInterpolator(method=self.interpolation_method)
                series = interp.transform(series)
                result["stages"]["after_interpolation"] = len(series)

                # 8. Persist: delete existing for store and insert new
                def _to_date(v: Any) -> date:
                    if isinstance(v, date) and not isinstance(v, datetime):
                        return v
                    if hasattr(v, "isoformat"):
                        return v.date() if isinstance(v, datetime) else v
                    return pd.Timestamp(v).date()

                session.query(NormalizedSeries).filter(
                    NormalizedSeries.store_id == self.store_id
                ).delete()
                for _, row in series.iterrows():
                    session.add(
                        NormalizedSeries(
                            store_id=row["store_id"],
                            sku_id=row["sku_id"],
                            category_id=row.get("category_id"),
                            series_date=_to_date(row["series_date"]),
                            quantity=float(row["quantity"]),
                            revenue=float(row["revenue"]),
                            is_interpolated=bool(row.get("is_interpolated", False)),
                            is_outlier_adjusted=bool(row.get("is_outlier_adjusted", False)),
                        )
                    )
                result["output_rows"] = len(series)
                return result
            except Exception as e:
                logger.exception("Pipeline failed for store %s", self.store_id)
                result["error"] = str(e)
                raise
