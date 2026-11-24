"""Vectorized data cleaning and feature engineering for the Mumbai & Thane real estate dataset."""

from pathlib import Path
from typing import Union

import numpy as np
import pandas as pd

from analytics.config import (
    KEY_AMENITIES,
    REALESTATE_DATA_PATH,
    RESIDENTIAL_TYPES,
    TARGET_CITIES,
)


def load_realestate_data(filepath: Union[str, Path] = REALESTATE_DATA_PATH) -> pd.DataFrame:
    """Load the raw real estate property listings CSV."""
    return pd.read_csv(filepath, low_memory=False)


def parse_amenity_series(series: pd.Series, amenity_name: str) -> pd.Series:
    """Convert raw amenity values (Y/N, 1/0, or descriptive parking strings) into binary 0/1."""
    series_str = series.astype(str).str.strip().str.upper()
    if amenity_name == "Parking":
        return (
            series_str.str.contains("COVERED|OPEN", regex=True, na=False)
            & ~series_str.str.contains("NAN", na=False)
        ).astype(int)

    mapping = {
        "Y": 1,
        "YES": 1,
        "1": 1,
        "1.0": 1,
        "TRUE": 1,
        "N": 0,
        "NO": 0,
        "0": 0,
        "0.0": 0,
        "FALSE": 0,
        "NAN": 0,
        "NONE": 0,
    }
    return series_str.map(mapping).fillna(0).astype(int)


def extract_availability_year(series: pd.Series) -> pd.Series:
    """Vectorized extraction of 4-digit availability year from strings like \"Dec '25\"."""
    s = series.astype(str).str.strip()
    two_digit = s.str.extract(r"'(\d{2})", expand=False)
    four_digit = s.str.extract(r"(\d{4})", expand=False)
    years = pd.to_numeric(four_digit, errors="coerce")
    two_digit_num = pd.to_numeric(two_digit, errors="coerce") + 2000
    return years.fillna(two_digit_num)


def preprocess_realestate_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean, impute, and engineer investment analytics features for Mumbai & Thane properties."""
    cleaned = df.copy()

    # Vectorized numeric cleaning
    cleaned["Price_Clean"] = pd.to_numeric(
        cleaned["Price"].astype(str).str.replace(",", "", regex=False),
        errors="coerce",
    )
    cleaned["Carpet_Area_Clean"] = pd.to_numeric(cleaned["Carpet Area"], errors="coerce")

    sqft_col = "sqft Price " if "sqft Price " in cleaned.columns else "sqft Price"
    cleaned["sqft_Price_Clean"] = pd.to_numeric(cleaned[sqft_col], errors="coerce")

    # Impute missing price per sq ft using Price / Carpet Area where valid
    impute_mask = (
        cleaned["sqft_Price_Clean"].isna()
        & cleaned["Price_Clean"].notna()
        & cleaned["Carpet_Area_Clean"].notna()
        & (cleaned["Carpet_Area_Clean"] > 0)
    )
    cleaned.loc[impute_mask, "sqft_Price_Clean"] = (
        cleaned.loc[impute_mask, "Price_Clean"]
        / cleaned.loc[impute_mask, "Carpet_Area_Clean"]
    )

    # Bedroom configuration & market segment
    cleaned["Bedroom_Category"] = (
        pd.to_numeric(cleaned["bedroom"], errors="coerce").fillna(0).astype(int).astype(str)
        + " BHK"
    )
    cleaned["Segment"] = np.where(
        cleaned["Type of Property"].isin(RESIDENTIAL_TYPES),
        "Residential",
        "Commercial",
    )

    # Filter to Mumbai & Thane metropolitan markets
    filtered = cleaned[cleaned["City"].isin(TARGET_CITIES)].copy()

    # Quantile-based price segmentation (33rd & 67th percentiles)
    q33, q67 = filtered["Price_Clean"].quantile([0.33, 0.67]).values
    filtered["Price_Segment"] = pd.cut(
        filtered["Price_Clean"],
        bins=[-np.inf, q33, q67, np.inf],
        labels=["Budget (Low)", "Mid-Range", "Premium (High)"],
    )

    # Location tier
    if "isPrimeLocationProperty" in filtered.columns:
        filtered["Location_Type"] = filtered["isPrimeLocationProperty"].map(
            {"Y": "Prime Location", "N": "Non-Prime Location"}
        )

    # Value score: Carpet Area (sq ft) per ₹ Lakh
    filtered["Value_Score"] = np.where(
        filtered["Price_Clean"] > 0,
        filtered["Carpet_Area_Clean"] / (filtered["Price_Clean"] / 100_000),
        np.nan,
    )

    # Binary amenity indicators
    for amenity in KEY_AMENITIES:
        if amenity in filtered.columns:
            filtered[f"{amenity}_Binary"] = parse_amenity_series(filtered[amenity], amenity)

    # Availability year for under-construction timelines
    if "Availability Starts From" in filtered.columns:
        filtered["Availability_Year"] = extract_availability_year(
            filtered["Availability Starts From"]
        )

    return filtered
