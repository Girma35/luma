"""
SKU deduplication: map raw SKU/variant IDs to canonical SKU using mapping table.
"""

import logging
from typing import Optional

import pandas as pd
from sqlalchemy.orm import Session

from src.db.models import SKUMapping

logger = logging.getLogger(__name__)


class SKUDeduplicator:
    """
    Resolves sku_raw to canonical_sku via store's SKU mapping table.
    If no mapping exists, uses sku_raw as canonical (pass-through).
    """

    def __init__(self, session: Session, store_id: str):
        self.session = session
        self.store_id = store_id
        self._mapping: Optional[dict[str, str]] = None

    def _load_mapping(self) -> dict[str, str]:
        if self._mapping is not None:
            return self._mapping
        rows = (
            self.session.query(SKUMapping.sku_raw, SKUMapping.canonical_sku)
            .filter(
                SKUMapping.store_id == self.store_id,
            )
            .all()
        )
        self._mapping = {r.sku_raw: r.canonical_sku for r in rows}
        return self._mapping

    def transform(self, orders: pd.DataFrame) -> pd.DataFrame:
        if orders.empty:
            orders["canonical_sku"] = pd.Series(dtype=str)
            return orders
        mapping = self._load_mapping()
        orders["canonical_sku"] = orders["sku_raw"].map(
            lambda x: mapping.get(x, x) if pd.notna(x) else ""
        )
        return orders
