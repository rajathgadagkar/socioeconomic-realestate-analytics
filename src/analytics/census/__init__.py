"""Adult Census socio-economic analytics subpackage."""

from .preprocessing import load_census_data, preprocess_census_data
from .analysis import run_census_analysis
from .visualization import generate_census_figures

__all__ = [
    "load_census_data",
    "preprocess_census_data",
    "run_census_analysis",
    "generate_census_figures",
]
