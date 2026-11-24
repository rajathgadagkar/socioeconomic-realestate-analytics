"""Publication-ready visualizations for the Adult Census socio-economic analysis."""

from pathlib import Path
from typing import List, Union

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from analytics.config import AGE_LABELS, DEFAULT_FIGURES_DIR


def _save_fig(fig: plt.Figure, output_dir: Path, filename: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / filename
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out_path


def generate_census_figures(
    df: pd.DataFrame,
    output_dir: Union[str, Path] = DEFAULT_FIGURES_DIR,
) -> List[Path]:
    """Generate and save all Adult Census analytical visualizations."""
    sns.set_theme(style="whitegrid")
    out_dir = Path(output_dir)
    saved: List[Path] = []

    # 1. Raw vs Grouped Education Comparison
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
    df["Education"].fillna("Missing").value_counts().plot(kind="bar", ax=ax1, color="#4C72B0")
    ax1.set_title("Raw Education Level Frequencies")
    ax1.set_ylabel("Count")
    ax1.tick_params(axis="x", rotation=45)

    df["Education_clean"].value_counts().plot(kind="bar", ax=ax2, color="#55A868")
    ax2.set_title("Grouped Education Attainment Tiers")
    ax2.set_ylabel("Count")
    ax2.tick_params(axis="x", rotation=35)
    fig.tight_layout()
    saved.append(_save_fig(fig, out_dir, "census_education_comparison.png"))

    # 2. Age & Weekly Hours Distributions
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.5))
    sns.histplot(df["Age"].dropna(), bins=30, kde=True, ax=ax1, color="#4C72B0")
    ax1.set_title("Age Distribution")
    sns.histplot(df["Hours_per_week"].dropna(), bins=30, kde=True, ax=ax2, color="#DD8452")
    ax2.set_title("Weekly Work Hours Distribution")
    fig.tight_layout()
    saved.append(_save_fig(fig, out_dir, "census_age_hours_distributions.png"))

    # 3. Age Group x Work Intensity Heatmap
    ct = pd.crosstab(df["age_group"], df["hours_group"])
    prop_ct = ct.div(ct.sum(axis=1), axis=0)
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.heatmap(prop_ct, annot=True, fmt=".2f", cmap="Blues", ax=ax)
    ax.set_title("Proportion of Work Intensity Within Each Life-Stage Age Group")
    fig.tight_layout()
    saved.append(_save_fig(fig, out_dir, "census_age_hours_heatmap.png"))

    # 4. Capital Activity Rate & Mean Net Capital (Age vs Work Intensity)
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    sns.barplot(x="age_group", y="capital_any", data=df, order=AGE_LABELS, color="steelblue", alpha=0.8, ax=axes[0, 0])
    axes[0, 0].set_title("Capital Activity Rate by Age Group")
    axes[0, 0].tick_params(axis="x", rotation=40)

    sns.barplot(x="age_group", y="net_capital", data=df, order=AGE_LABELS, color="#C44E52", alpha=0.8, ax=axes[0, 1])
    axes[0, 1].set_title("Mean Net Capital ($) by Age Group")
    axes[0, 1].tick_params(axis="x", rotation=40)

    hours_order = [
        h for h in ["Minimal Hours", "Part-time", "Full-time", "Overtime", "Heavy-overtime"]
        if h in df["hours_group"].unique()
    ]
    sns.barplot(x="hours_group", y="capital_any", data=df, order=hours_order, color="forestgreen", alpha=0.8, ax=axes[1, 0])
    axes[1, 0].set_title("Capital Activity Rate by Work Intensity")
    axes[1, 0].tick_params(axis="x", rotation=25)

    sns.barplot(x="hours_group", y="net_capital", data=df, order=hours_order, color="darkorange", alpha=0.8, ax=axes[1, 1])
    axes[1, 1].set_title("Mean Net Capital ($) by Work Intensity")
    axes[1, 1].tick_params(axis="x", rotation=25)

    fig.suptitle("Capital Activity & Net Capital Across Life Stages and Work Intensity", fontsize=14, fontweight="bold")
    fig.tight_layout()
    saved.append(_save_fig(fig, out_dir, "census_capital_activity.png"))

    return saved
