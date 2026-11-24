"""Vectorized data loading and feature engineering for the Adult Census dataset."""

from pathlib import Path
from typing import Union

import numpy as np
import pandas as pd

from analytics.config import (
    AGE_BINS,
    AGE_LABELS,
    CENSUS_DATA_PATH,
    EDUCATION_MAP,
    HOURS_BINS,
    HOURS_LABELS,
)


def load_census_data(filepath: Union[str, Path] = CENSUS_DATA_PATH) -> pd.DataFrame:
    """Load the Adult Census CSV while stripping leading whitespace."""
    return pd.read_csv(filepath, skipinitialspace=True)


def preprocess_census_data(df: pd.DataFrame) -> pd.DataFrame:
    """Apply vectorized cleaning, grouping, and capital feature engineering.

    Engineered columns:
        - Education_clean: Consolidated 6-tier educational attainment hierarchy
        - age_group: 8 life-stage categories
        - hours_group: Work-intensity bands aligned with employment norms
        - net_capital: Capital_Gain - Capital_Loss
        - capital_any: Boolean indicator for any capital market activity
    """
    cleaned = df.copy()

    # Coerce numeric columns cleanly
    for col in ("Age", "Hours_per_week", "Capital_Gain", "Capital_Loss"):
        if col in cleaned.columns:
            cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce")

    cleaned["Capital_Gain"] = cleaned["Capital_Gain"].fillna(0.0)
    cleaned["Capital_Loss"] = cleaned["Capital_Loss"].fillna(0.0)

    # 1. Consolidate education levels (vectorized map)
    edu_series = cleaned["Education"].fillna("Missing").astype(str).str.strip()
    cleaned["Education_clean"] = edu_series.map(EDUCATION_MAP).fillna(edu_series)

    # 2. Bin continuous age into life-stage segments
    cleaned["age_group"] = pd.cut(
        cleaned["Age"],
        bins=AGE_BINS,
        labels=AGE_LABELS,
        right=True,
        include_lowest=True,
    )

    # 3. Bin continuous weekly hours into work-intensity categories
    hours_cat = pd.cut(
        cleaned["Hours_per_week"],
        bins=HOURS_BINS,
        labels=HOURS_LABELS,
        right=True,
    )
    cleaned["hours_group"] = hours_cat.astype(object).fillna("Missing")

    # 4. Derive net capital & participation flag
    cleaned["net_capital"] = cleaned["Capital_Gain"] - cleaned["Capital_Loss"]
    cleaned["capital_any"] = (cleaned["Capital_Gain"] > 0) | (cleaned["Capital_Loss"] > 0)

    return cleaned
