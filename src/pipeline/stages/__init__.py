"""
ReOrder AI — Pipeline stages (normalizers).
Each stage is a callable or class that transforms DataFrame in place or returns a new one.
"""

from src.pipeline.stages.timezone import TimezoneNormalizer
from src.pipeline.stages.currency import CurrencyNormalizer
from src.pipeline.stages.dedup import SKUDeduplicator
from src.pipeline.stages.rollups import VariantRollup
from src.pipeline.stages.refunds import RefundAdjustment
from src.pipeline.stages.outliers import OutlierDetector
from src.pipeline.stages.interpolation import MissingDataInterpolator

__all__ = [
    "TimezoneNormalizer",
    "CurrencyNormalizer",
    "SKUDeduplicator",
    "VariantRollup",
    "RefundAdjustment",
    "OutlierDetector",
    "MissingDataInterpolator",
]
