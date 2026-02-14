"""
Outlier detection: flag or cap extreme values in the time-series (e.g. bulk orders, typos).
"""

import logging
from typing import Literal

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class OutlierDetector:
    """
    Uses IQR (interquartile range) to detect and optionally cap outliers in quantity and revenue.
    Strategy: 'cap' replaces values beyond bounds with the bound; 'flag' only sets is_outlier_adjusted.
    """

    def __init__(
        self,
        strategy: Literal["cap", "flag", "none"] = "cap",
        iqr_multiplier: float = 1.5,
    ):
        self.strategy = strategy
        self.iqr_multiplier = iqr_multiplier

    def transform(self, series: pd.DataFrame) -> pd.DataFrame:
        if series.empty or self.strategy == "none":
            return series
        for col in ["quantity", "revenue"]:
            if col not in series.columns:
                continue
            q1 = series[col].quantile(0.25)
            q3 = series[col].quantile(0.75)
            iqr = q3 - q1
            if iqr == 0:
                continue
            low = q1 - self.iqr_multiplier * iqr
            high = q3 + self.iqr_multiplier * iqr
            if self.strategy == "cap":
                adjusted = (series[col] < low) | (series[col] > high)
                series.loc[adjusted, col] = series.loc[adjusted, col].clip(low, high)
                series.loc[adjusted, "is_outlier_adjusted"] = True
            else:
                series["is_outlier_adjusted"] = series["is_outlier_adjusted"] | (
                    (series[col] < low) | (series[col] > high)
                )
        return series
