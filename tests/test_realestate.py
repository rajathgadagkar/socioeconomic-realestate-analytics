"""Unit tests for the Mumbai & Thane real estate preprocessing module."""

import pandas as pd

from analytics.realestate.preprocessing import (
    extract_availability_year,
    parse_amenity_series,
    preprocess_realestate_data,
)


def test_parse_amenity_series_handles_mixed_and_parking_formats():
    yn = pd.Series(["Y", "N", "1", "0", None])
    assert list(parse_amenity_series(yn, "Swimming Pool")) == [1, 0, 1, 0, 0]

    parking = pd.Series(["1 Covered", "1 Open", None, "None"])
    assert list(parse_amenity_series(parking, "Parking")) == [1, 1, 0, 0]


def test_extract_availability_year():
    dates = pd.Series(["Dec '25", "Mar '27", "2026", None])
    years = extract_availability_year(dates)
    assert years.iloc[0] == 2025
    assert years.iloc[1] == 2027
    assert years.iloc[2] == 2026
    assert pd.isna(years.iloc[3])


def test_preprocess_realestate_imputes_sqft_and_filters_cities():
    sample = pd.DataFrame(
        {
            "City": ["Mumbai", "Thane", "Pune"],
            "Price": ["10,000,000", "5,000,000", "4,000,000"],
            "Carpet Area": [500, 500, 500],
            "sqft Price ": [None, 10000, 8000],
            "bedroom": [2, 1, 2],
            "Type of Property": ["Apartment", "Apartment", "Apartment"],
            "isPrimeLocationProperty": ["Y", "N", "Y"],
        }
    )
    out = preprocess_realestate_data(sample)
    assert len(out) == 2
    assert out.iloc[0]["sqft_Price_Clean"] == 20000.0
    assert out.iloc[0]["Value_Score"] == 5.0
    assert out.iloc[1]["Value_Score"] == 10.0
