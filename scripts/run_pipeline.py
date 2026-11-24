#!/usr/bin/env python3
"""Unified CLI entry point for running the Socio-Economic & Real Estate Analytics pipeline."""

import argparse
import json
import sys
from pathlib import Path

# Allow running directly without editable install
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from analytics.census import (
    generate_census_figures,
    load_census_data,
    preprocess_census_data,
    run_census_analysis,
)
from analytics.config import DEFAULT_OUTPUT_DIR
from analytics.realestate import (
    generate_realestate_figures,
    load_realestate_data,
    preprocess_realestate_data,
    run_realestate_analysis,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the Socio-Economic Demographics & Real Estate Investment Analytics pipeline."
    )
    parser.add_argument(
        "--module",
        choices=("all", "census", "realestate"),
        default="all",
        help="Which analytical module to execute (default: all).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for JSON summary reports and generated figures.",
    )
    parser.add_argument(
        "--skip-plots",
        action="store_true",
        help="Skip figure generation and compute statistical summaries only.",
    )
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    figures_dir = args.output_dir / "figures"
    results = {}

    if args.module in ("all", "census"):
        print("▶ Running Adult Census Socio-Economic Analytics...")
        census_raw = load_census_data()
        census_clean = preprocess_census_data(census_raw)
        results["census"] = run_census_analysis(census_clean)
        if not args.skip_plots:
            figs = generate_census_figures(census_clean, output_dir=figures_dir)
            print(f"  ✓ Saved {len(figs)} census figures to {figures_dir}")

    if args.module in ("all", "realestate"):
        print("▶ Running Mumbai & Thane Real Estate Investment Analytics...")
        re_raw = load_realestate_data()
        re_clean = preprocess_realestate_data(re_raw)
        results["realestate"] = run_realestate_analysis(re_clean)
        if not args.skip_plots:
            figs = generate_realestate_figures(re_clean, output_dir=figures_dir)
            print(f"  ✓ Saved {len(figs)} real estate figures to {figures_dir}")

    report_path = args.output_dir / "analytics_summary.json"
    with report_path.open("w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, default=str)

    print(f"✓ Pipeline complete. Summary written to {report_path}")


if __name__ == "__main__":
    main()
