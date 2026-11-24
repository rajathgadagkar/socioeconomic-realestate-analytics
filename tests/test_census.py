"""Unit tests for the Adult Census preprocessing and statistical modules."""

import pandas as pd

from analytics.census.analysis import cramers_v
from analytics.census.preprocessing import preprocess_census_data


def test_preprocess_census_data_engineers_expected_features():
    sample = pd.DataFrame(
        {
            "Age": ["22", "48", "68"],
            "Education": ["HS-grad", "Masters", "7th-8th"],
            "Hours_per_week": [25, 45, 55],
            "Capital_Gain": [0, 5000, 0],
            "Capital_Loss": [0, 0, 1200],
        }
    )
    out = preprocess_census_data(sample)

    assert list(out["Education_clean"]) == [
        "High-school",
        "Postgraduate",
        "No/Low-education",
    ]
    assert list(out["age_group"]) == [
        "Young Adults (18-24)",
        "Experienced (45-54)",
        "Retirement Age (65-74)",
    ]
    assert list(out["hours_group"]) == ["Part-time", "Full-time", "Overtime"]
    assert list(out["net_capital"]) == [0.0, 5000.0, -1200.0]
    assert list(out["capital_any"]) == [False, True, True]


def test_cramers_v_bounds():
    ct = pd.DataFrame([[50, 5], [5, 50]])
    v = cramers_v(ct)
    assert 0.0 <= v <= 1.0
    assert v > 0.7
