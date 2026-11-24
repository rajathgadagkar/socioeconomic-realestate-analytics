"""Statistical analysis and modeling for the Adult Census socio-economic dataset."""

from typing import Any, Dict

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm

from analytics.config import AGE_LABELS


def cramers_v(confusion_matrix: pd.DataFrame) -> float:
    """Compute Cramér's V effect size for a contingency table."""
    chi2 = stats.chi2_contingency(confusion_matrix, correction=False)[0]
    n = confusion_matrix.sum().sum()
    r, k = confusion_matrix.shape
    denom = n * (min(r, k) - 1)
    return float(np.sqrt(chi2 / denom)) if denom > 0 else 0.0


def analyze_education(df: pd.DataFrame) -> Dict[str, Any]:
    """Summarize raw vs. grouped education distributions."""
    raw_counts = df["Education"].fillna("Missing").value_counts().to_dict()
    grouped_counts = df["Education_clean"].value_counts().to_dict()
    reduction_pct = ((len(raw_counts) - len(grouped_counts)) / max(len(raw_counts), 1)) * 100
    return {
        "raw_category_count": len(raw_counts),
        "grouped_category_count": len(grouped_counts),
        "category_reduction_pct": round(reduction_pct, 2),
        "grouped_distribution": grouped_counts,
    }


def analyze_age_work_relationship(df: pd.DataFrame) -> Dict[str, Any]:
    """Quantify continuous and grouped age vs. work-intensity associations."""
    valid = df[["Age", "Hours_per_week"]].dropna()
    spearman_rho, spearman_p = stats.spearmanr(valid["Age"], valid["Hours_per_week"])

    ct = pd.crosstab(df["age_group"], df["hours_group"])
    chi2, chi2_p, dof, _ = stats.chi2_contingency(ct, correction=False)
    cv = cramers_v(ct)

    return {
        "spearman_rho": round(float(spearman_rho), 4),
        "spearman_p_value": float(spearman_p),
        "chi2_statistic": round(float(chi2), 2),
        "chi2_p_value": float(chi2_p),
        "degrees_of_freedom": int(dof),
        "cramers_v": round(cv, 4),
    }


def analyze_capital_activity(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze capital gains/losses, group performance, and standardized regression drivers."""
    active = df[df["capital_any"]]
    gains = active[active["net_capital"] > 0]["net_capital"]
    losses = active[active["net_capital"] < 0]["net_capital"]

    # Non-parametric Kruskal-Wallis tests
    age_samples = [
        df.loc[df["age_group"] == g, "net_capital"].dropna().values for g in AGE_LABELS
    ]
    age_samples = [s for s in age_samples if len(s) > 0]
    kw_age = stats.kruskal(*age_samples)

    hours_order = ["Minimal Hours", "Part-time", "Full-time", "Overtime", "Heavy-overtime"]
    hours_samples = [
        df.loc[df["hours_group"] == h, "net_capital"].dropna().values for h in hours_order
    ]
    hours_samples = [s for s in hours_samples if len(s) > 0]
    kw_hours = stats.kruskal(*hours_samples)

    # Standardized Logistic Regression for participation probability
    reg_df = df[["capital_any", "Age", "Hours_per_week"]].dropna().copy()
    reg_df["Age_s"] = (reg_df["Age"] - reg_df["Age"].mean()) / reg_df["Age"].std()
    reg_df["Hours_s"] = (
        reg_df["Hours_per_week"] - reg_df["Hours_per_week"].mean()
    ) / reg_df["Hours_per_week"].std()

    logit_model = sm.Logit(
        reg_df["capital_any"].astype(int),
        sm.add_constant(reg_df[["Age_s", "Hours_s"]]),
    ).fit(disp=False)

    # Standardized OLS on log1p(positive net capital) among active participants
    mag_df = active[["net_capital", "Age", "Hours_per_week"]].dropna().copy()
    mag_df["log_net1p"] = np.log1p(mag_df["net_capital"].clip(lower=0))
    mag_df["Age_s"] = (mag_df["Age"] - mag_df["Age"].mean()) / mag_df["Age"].std()
    mag_df["Hours_s"] = (
        mag_df["Hours_per_week"] - mag_df["Hours_per_week"].mean()
    ) / mag_df["Hours_per_week"].std()

    ols_model = sm.OLS(
        mag_df["log_net1p"],
        sm.add_constant(mag_df[["Age_s", "Hours_s"]]),
    ).fit()

    age_summary = (
        df.groupby("age_group", observed=False)
        .agg(
            mean_net_capital=("net_capital", "mean"),
            activity_rate=("capital_any", "mean"),
            count=("net_capital", "size"),
        )
        .round(4)
        .to_dict(orient="index")
    )

    hours_summary = (
        df.groupby("hours_group", observed=False)
        .agg(
            mean_net_capital=("net_capital", "mean"),
            activity_rate=("capital_any", "mean"),
            count=("net_capital", "size"),
        )
        .round(4)
        .to_dict(orient="index")
    )

    return {
        "overall_activity_rate_pct": round(float(df["capital_any"].mean() * 100), 2),
        "active_count": int(len(active)),
        "pure_gains_count": int(len(gains)),
        "pure_losses_count": int(len(losses)),
        "mean_gain_usd": round(float(gains.mean()), 2) if len(gains) else 0.0,
        "mean_loss_usd": round(float(losses.mean()), 2) if len(losses) else 0.0,
        "kruskal_wallis_age": {
            "statistic": round(float(kw_age.statistic), 3),
            "p_value": float(kw_age.pvalue),
        },
        "kruskal_wallis_hours": {
            "statistic": round(float(kw_hours.statistic), 3),
            "p_value": float(kw_hours.pvalue),
        },
        "logit_standardized_coefficients": {
            "age": round(float(logit_model.params["Age_s"]), 4),
            "hours_per_week": round(float(logit_model.params["Hours_s"]), 4),
            "pseudo_r2": round(float(logit_model.prsquared), 4),
            "stronger_driver": (
                "Age"
                if abs(logit_model.params["Age_s"]) > abs(logit_model.params["Hours_s"])
                else "Hours_per_week"
            ),
        },
        "ols_log_magnitude_coefficients": {
            "age": round(float(ols_model.params["Age_s"]), 4),
            "hours_per_week": round(float(ols_model.params["Hours_s"]), 4),
            "r_squared": round(float(ols_model.rsquared), 4),
        },
        "by_age_group": {str(k): v for k, v in age_summary.items()},
        "by_hours_group": {str(k): v for k, v in hours_summary.items()},
    }


def run_census_analysis(df: pd.DataFrame) -> Dict[str, Any]:
    """Execute the complete Adult Census statistical analysis suite."""
    return {
        "dataset_shape": {"rows": int(df.shape[0]), "columns": int(df.shape[1])},
        "education": analyze_education(df),
        "age_work_intensity": analyze_age_work_relationship(df),
        "capital_activity": analyze_capital_activity(df),
    }
