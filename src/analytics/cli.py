"""Packaged CLI wrapper for the analytics pipeline."""

import argparse
import json
from pathlib import Path

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
        help="Analytical module to run (default: all).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Output directory for summary JSON and figures.",
    )
    parser.add_argument(
        "--skip-plots",
        action="store_true",
        help="Skip plot generation.",
    )
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    figures_dir = args.output_dir / "figures"
    results = {}

    if args.module in ("all", "census"):
        census_clean = preprocess_census_data(load_census_data())
        results["census"] = run_census_analysis(census_clean)
        if not args.skip_plots:
            generate_census_figures(census_clean, output_dir=figures_dir)

    if args.module in ("all", "realestate"):
        re_clean = preprocess_realestate_data(load_realestate_data())
        results["realestate"] = run_realestate_analysis(re_clean)
        if not args.skip_plots:
            generate_realestate_figures(re_clean, output_dir=figures_dir)

    report_path = args.output_dir / "analytics_summary.json"
    with report_path.open("w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, default=str)
    print(f"Summary written to {report_path}")


if __name__ == "__main__":
    main()
