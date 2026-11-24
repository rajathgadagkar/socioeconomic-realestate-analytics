"""Centralized configuration, paths, and domain mappings for the analytics pipeline."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "outputs"
DEFAULT_FIGURES_DIR = PROJECT_ROOT / "docs" / "figures"

CENSUS_DATA_PATH = DATA_RAW_DIR / "adult_census.csv"
REALESTATE_DATA_PATH = DATA_RAW_DIR / "mumbai_thane_realestate.csv"

EDUCATION_MAP = {
    "Preschool": "No/Low-education",
    "1st-4th": "No/Low-education",
    "5th-6th": "No/Low-education",
    "7th-8th": "No/Low-education",
    "9th": "Secondary-incomplete",
    "10th": "Secondary-incomplete",
    "11th": "Secondary-incomplete",
    "12th": "Secondary-incomplete",
    "HS-grad": "High-school",
    "Some-college": "College-non-degree",
    "Assoc-acdm": "College-non-degree",
    "Assoc-voc": "College-non-degree",
    "Bachelors": "Bachelors",
    "Masters": "Postgraduate",
    "Prof-school": "Postgraduate",
    "Doctorate": "Postgraduate",
    "Missing": "Missing",
}

EDUCATION_ORDER = [
    "No/Low-education",
    "Secondary-incomplete",
    "High-school",
    "College-non-degree",
    "Bachelors",
    "Postgraduate",
    "Missing",
]

AGE_BINS = [0, 17, 24, 34, 44, 54, 64, 74, 200]
AGE_LABELS = [
    "Adolescents (0-17)",
    "Young Adults (18-24)",
    "Early Career (25-34)",
    "Mid Career (35-44)",
    "Experienced (45-54)",
    "Late Career (55-64)",
    "Retirement Age (65-74)",
    "Seniors (75+)",
]

HOURS_BINS = [-1, 0, 15, 34, 50, 60, 200]
HOURS_LABELS = [
    "Unemployed/0",
    "Minimal Hours",
    "Part-time",
    "Full-time",
    "Overtime",
    "Heavy-overtime",
]

TARGET_CITIES = ("Mumbai", "Thane")
RESIDENTIAL_TYPES = ("Apartment", "Villa", "Independent House", "Builder Floor")
KEY_AMENITIES = (
    "Swimming Pool",
    "Gymnasium",
    "Club House",
    "Security",
    "Lift",
    "Parking",
    "Power Back Up",
    "Water Storage",
    "Park",
)
