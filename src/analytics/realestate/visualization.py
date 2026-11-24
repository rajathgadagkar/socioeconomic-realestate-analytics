"""Publication-ready visualizations for Mumbai & Thane real estate investment analytics."""

from pathlib import Path
from typing import List, Union

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from analytics.config import DEFAULT_FIGURES_DIR
from analytics.realestate.analysis import analyze_controlled_amenity_impact


def _save_fig(fig: plt.Figure, output_dir: Path, filename: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / filename
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out_path


def generate_realestate_figures(
    df: pd.DataFrame,
    output_dir: Union[str, Path] = DEFAULT_FIGURES_DIR,
) -> List[Path]:
    """Generate and save core real estate market visualizations."""
    sns.set_theme(style="whitegrid")
    out_dir = Path(output_dir)
    saved: List[Path] = []

    # 1. Price Segments by City & Average Price
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    pd.crosstab(df["City"], df["Price_Segment"]).plot(
        kind="bar", ax=ax1, color=["#FF9999", "#66B2FF", "#99FF99"]
    )
    ax1.set_title("Price Segment Distribution by City")
    ax1.set_ylabel("Number of Properties")
    ax1.tick_params(axis="x", rotation=0)

    df.groupby(["Price_Segment", "City"], observed=False)["Price_Clean"].mean().unstack().plot(
        kind="bar", ax=ax2, color=["#FF6B6B", "#4ECDC4"]
    )
    ax2.set_title("Average Property Price by Segment & City (₹ Crores)")
    ax2.set_ylabel("Average Price (₹ Crores)")
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"₹{x / 1e7:.1f}"))
    ax2.tick_params(axis="x", rotation=20)
    fig.tight_layout()
    saved.append(_save_fig(fig, out_dir, "realestate_price_segments.png"))

    # 2. Prime vs Non-Prime Location Price per sq ft
    loc_df = df[df["Location_Type"].notna()]
    fig, ax = plt.subplots(figsize=(8, 5))
    loc_df.groupby(["City", "Location_Type"])["sqft_Price_Clean"].mean().unstack().plot(
        kind="bar", ax=ax, color=["#FFB366", "#66FFB2"]
    )
    ax.set_title("Average Price per sq ft: Prime vs Non-Prime Locations")
    ax.set_ylabel("Price per sq ft (₹)")
    ax.tick_params(axis="x", rotation=0)
    fig.tight_layout()
    saved.append(_save_fig(fig, out_dir, "realestate_location_premium.png"))

    # 3. Value-for-Money Top 10 Areas
    q95 = df["Value_Score"].quantile(0.95)
    val_df = df[(df["Value_Score"] > 0) & (df["Value_Score"] < q95)]
    fig, ax = plt.subplots(figsize=(10, 5))
    val_df.groupby("Area Name")["Value_Score"].mean().nlargest(10).plot(
        kind="bar", ax=ax, color="#4C72B0"
    )
    ax.set_title("Top 10 Localities by Average Value Score (sq ft per ₹ Lakh)")
    ax.set_ylabel("Average Value Score (sq ft / ₹ Lakh)")
    ax.tick_params(axis="x", rotation=35)
    fig.tight_layout()
    saved.append(_save_fig(fig, out_dir, "realestate_top_value_areas.png"))

    # 4. Controlled Amenity Impact on Price per sq ft
    impacts = analyze_controlled_amenity_impact(df)
    if impacts:
        imp_series = pd.Series({k: v["controlled_sqft_impact_pct"] for k, v in impacts.items()})
        fig, ax = plt.subplots(figsize=(10, 5))
        colors = ["#55A868" if v >= 0 else "#C44E52" for v in imp_series.values]
        imp_series.plot(kind="barh", ax=ax, color=colors)
        ax.axvline(0, color="black", linewidth=0.8)
        ax.set_title("Size-Controlled Amenity Impact on Price per sq ft (%)")
        ax.set_xlabel("Controlled Price/sq ft Impact (%)")
        fig.tight_layout()
        saved.append(_save_fig(fig, out_dir, "realestate_amenity_impact.png"))

    return saved
