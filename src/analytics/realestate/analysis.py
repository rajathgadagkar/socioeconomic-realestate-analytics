"""Market intelligence and investment analytics for Mumbai & Thane real estate."""

from typing import Any, Dict

import numpy as np
import pandas as pd

from analytics.config import KEY_AMENITIES, TARGET_CITIES


def analyze_price_segments(df: pd.DataFrame) -> Dict[str, Any]:
    """Summarize budget, mid-range, and premium market segments."""
    summary = {}
    for seg in ("Budget (Low)", "Mid-Range", "Premium (High)"):
        sub = df[df["Price_Segment"] == seg]
        summary[seg] = {
            "count": int(len(sub)),
            "avg_price_lakhs": round(float(sub["Price_Clean"].mean() / 100_000), 2),
            "avg_carpet_area_sqft": round(float(sub["Carpet_Area_Clean"].mean()), 1),
            "city_split": {k: int(v) for k, v in sub["City"].value_counts().to_dict().items()},
        }
    return summary


def analyze_city_comparison(df: pd.DataFrame) -> Dict[str, Any]:
    """Compare Mumbai and Thane across price, area, and price per sq ft."""
    city_stats: Dict[str, Any] = {}
    for city in TARGET_CITIES:
        sub = df[df["City"] == city]
        city_stats[city] = {
            "count": int(len(sub)),
            "avg_price_lakhs": round(float(sub["Price_Clean"].mean() / 100_000), 2),
            "median_price_lakhs": round(float(sub["Price_Clean"].median() / 100_000), 2),
            "avg_carpet_area_sqft": round(float(sub["Carpet_Area_Clean"].mean()), 1),
            "avg_price_per_sqft_inr": round(float(sub["sqft_Price_Clean"].mean()), 1),
        }

    mum_sqft = city_stats["Mumbai"]["avg_price_per_sqft_inr"]
    thn_sqft = city_stats["Thane"]["avg_price_per_sqft_inr"]
    city_stats["thane_sqft_cost_advantage_pct"] = round(
        ((mum_sqft - thn_sqft) / mum_sqft) * 100, 2
    )
    return city_stats


def analyze_location_premium(df: pd.DataFrame) -> Dict[str, Any]:
    """Quantify prime vs. non-prime location price premiums per city."""
    results: Dict[str, Any] = {}
    valid = df[df["Location_Type"].notna()]
    for city in TARGET_CITIES:
        sub = valid[valid["City"] == city]
        prime = sub[sub["Location_Type"] == "Prime Location"]
        non_prime = sub[sub["Location_Type"] == "Non-Prime Location"]
        if len(prime) and len(non_prime):
            p_price = prime["Price_Clean"].mean()
            np_price = non_prime["Price_Clean"].mean()
            p_sqft = prime["sqft_Price_Clean"].mean()
            np_sqft = non_prime["sqft_Price_Clean"].mean()
            results[city] = {
                "prime_count": int(len(prime)),
                "non_prime_count": int(len(non_prime)),
                "price_premium_pct": round(float(((p_price - np_price) / np_price) * 100), 2),
                "sqft_price_premium_pct": round(float(((p_sqft - np_sqft) / np_sqft) * 100), 2),
            }
    return results


def analyze_value_for_money(df: pd.DataFrame) -> Dict[str, Any]:
    """Rank cities and top localities by Carpet Area per ₹ Lakh (Value Score)."""
    q95 = df["Value_Score"].quantile(0.95)
    valid = df[(df["Value_Score"] > 0) & (df["Value_Score"] < q95)]
    city_medians = valid.groupby("City")["Value_Score"].median().round(2).to_dict()
    top_areas = (
        valid.groupby("Area Name")["Value_Score"]
        .mean()
        .nlargest(10)
        .round(2)
        .to_dict()
    )
    return {
        "properties_analyzed": int(len(valid)),
        "top_quartile_threshold": round(float(valid["Value_Score"].quantile(0.75)), 2),
        "city_median_value_score": {k: float(v) for k, v in city_medians.items()},
        "top_10_areas": {k: float(v) for k, v in top_areas.items()},
    }


def analyze_controlled_amenity_impact(df: pd.DataFrame) -> Dict[str, Any]:
    """Estimate size-controlled (price/sq ft) impact of amenities controlling for other amenities."""
    valid = df[df["Price_Clean"].notna() & (df["sqft_Price_Clean"] > 0)].copy()
    binary_cols = [f"{a}_Binary" for a in KEY_AMENITIES if f"{a}_Binary" in valid.columns]
    impacts: Dict[str, Any] = {}

    for amenity in KEY_AMENITIES:
        col = f"{amenity}_Binary"
        if col not in valid.columns:
            continue
        other_cols = [c for c in binary_cols if c != col]
        other_count = valid[other_cols].sum(axis=1)
        with_df = valid[valid[col] == 1]
        without_df = valid[valid[col] == 0]
        if len(with_df) <= 10 or len(without_df) <= 10:
            continue

        comparisons = []
        for cnt in range(int(other_count.max()) + 1):
            w = with_df[other_count.loc[with_df.index] == cnt]
            wo = without_df[other_count.loc[without_df.index] == cnt]
            if len(w) >= 3 and len(wo) >= 3:
                comparisons.append(
                    (w["sqft_Price_Clean"].mean(), wo["sqft_Price_Clean"].mean(), len(w) + len(wo))
                )

        if comparisons:
            total_w = sum(c[2] for c in comparisons)
            controlled_pct = sum(((c[0] - c[1]) / c[1] * 100) * (c[2] / total_w) for c in comparisons)
        else:
            controlled_pct = (
                (with_df["sqft_Price_Clean"].mean() - without_df["sqft_Price_Clean"].mean())
                / without_df["sqft_Price_Clean"].mean()
            ) * 100

        impacts[amenity] = {
            "controlled_sqft_impact_pct": round(float(controlled_pct), 2),
            "avg_sqft_with_inr": round(float(with_df["sqft_Price_Clean"].mean()), 1),
            "avg_sqft_without_inr": round(float(without_df["sqft_Price_Clean"].mean()), 1),
        }

    return dict(sorted(impacts.items(), key=lambda kv: kv[1]["controlled_sqft_impact_pct"], reverse=True))


def analyze_possession_timeline(df: pd.DataFrame) -> Dict[str, Any]:
    """Compare Ready-to-Move vs. Under-Construction pricing across Mumbai and Thane."""
    results: Dict[str, Any] = {}
    for city in TARGET_CITIES:
        sub = df[df["City"] == city]
        rtm = sub[sub["Possession Status"] == "Ready to Move"]["Price_Clean"].dropna()
        uc = sub[sub["Possession Status"] == "Under Construction"]["Price_Clean"].dropna()
        if len(rtm) and len(uc):
            results[city] = {
                "ready_to_move_avg_lakhs": round(float(rtm.mean() / 100_000), 2),
                "under_construction_avg_lakhs": round(float(uc.mean() / 100_000), 2),
                "ready_to_move_premium_pct": round(
                    float(((rtm.mean() - uc.mean()) / uc.mean()) * 100), 2
                ),
            }
    return results


def analyze_developers(df: pd.DataFrame) -> Dict[str, Any]:
    """Segment active developers (5+ properties) into pricing tiers and compute consistency."""
    dev_df = df[df["Developer"].notna() & ~df["Developer"].isin(["NA", ""])].copy()
    stats_df = dev_df.groupby("Developer").agg(
        property_count=("Price_Clean", "count"),
        avg_price=("Price_Clean", "mean"),
        price_std=("Price_Clean", "std"),
        avg_sqft_price=("sqft_Price_Clean", "mean"),
    )
    sig = stats_df[stats_df["property_count"] >= 5].copy()
    sig["avg_price_lakhs"] = sig["avg_price"] / 100_000
    sig["price_cv_pct"] = (sig["price_std"] / sig["avg_price"]) * 100

    top_volume = sig.nlargest(10, "property_count")["property_count"].to_dict()
    return {
        "valid_developer_listings": int(len(dev_df)),
        "significant_developers_count": int(len(sig)),
        "top_10_by_volume": {k: int(v) for k, v in top_volume.items()},
    }


def run_realestate_analysis(df: pd.DataFrame) -> Dict[str, Any]:
    """Execute the complete Mumbai & Thane real estate investment analytics suite."""
    return {
        "total_properties_analyzed": int(len(df)),
        "price_segments": analyze_price_segments(df),
        "city_comparison": analyze_city_comparison(df),
        "location_premium": analyze_location_premium(df),
        "value_for_money": analyze_value_for_money(df),
        "controlled_amenity_impact": analyze_controlled_amenity_impact(df),
        "possession_timeline": analyze_possession_timeline(df),
        "developer_landscape": analyze_developers(df),
    }
