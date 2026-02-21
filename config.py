"""
Shared configuration constants for wind power cannibalization analysis.

This module contains common parameters, file paths, and mappings
used across multiple analysis and visualization scripts.
"""

from pathlib import Path

# =============================================================================
# TEMPORAL CONFIGURATION
# =============================================================================

# Analysis period
START_YEAR = 2015
END_YEAR = 2024
YEARS = range(START_YEAR, END_YEAR + 1)

# =============================================================================
# COUNTRY AND REGION MAPPINGS
# =============================================================================

# Mapping of country codes to electricity price data filenames
PRICE_FILES = {
    "AT": "Austria.csv",
    "BE": "Belgium.csv",
    "BG": "Bulgaria.csv",
    "CH": "Switzerland.csv",
    "CZ": "Czech Republic.csv",
    "DE": "Germany.csv",
    "EE": "Estonia.csv",
    "ES": "Spain.csv",
    "FI": "Finland.csv",
    "FR": "France.csv",
    "GR": "Greece.csv",
    "HR": "Croatia.csv",
    "HU": "Hungary.csv",
    "LT": "Lithuania.csv",
    "LV": "Latvia.csv",
    "LU": "Luxembourg.csv",
    "NL": "Netherlands.csv",
    "PL": "Poland.csv",
    "PT": "Portugal.csv",
    "RO": "Romania.csv",
    "SI": "Slovenia.csv",
    "SK": "Slovakia.csv",
}

# Mapping of country codes to zonal price data filenames
ZONAL_FILES = {
    "DK": "Denmark.csv",
    "IT": "Italy.csv",
    "NO": "Norway.csv",
    "SE": "Sweden.csv",
}

# =============================================================================
# SPATIAL CONFIGURATION
# =============================================================================

# Default coordinate reference system
DEFAULT_CRS = "EPSG:4326"

# European domain extent [lon_min, lon_max, lat_min, lat_max]
EUROPE_EXTENT = [-12, 45, 35, 72]

# =============================================================================
# WIND POWER CONVERSION
# =============================================================================

# Standard measurement height for wind speed (meters)
WIND_MEASUREMENT_HEIGHT = 100

# Wind speed limits (m/s)
MIN_WIND_SPEED = 0.0
MAX_WIND_SPEED = 30.0

# Default turbine specifications
DEFAULT_CUT_IN_SPEED = 3.0  # m/s
DEFAULT_RATED_SPEED = 12.0  # m/s
DEFAULT_CUT_OUT_SPEED = 25.0  # m/s

# Maximum capacity factor (used for data validation)
MAX_CAPACITY_FACTOR = 0.95

# =============================================================================
# FILE PATHS (relative to project root)
# =============================================================================

# These can be overridden by command-line arguments in individual scripts
BASE_DIR = Path(__file__).resolve().parents[1]

# Data directories
DATA_DIR = BASE_DIR / "data"
DATA_RAW_DIR = DATA_DIR / "raw"
DATA_PROCESSED_DIR = DATA_DIR / "processed"

# Input data paths
NETCDF_DIR = DATA_RAW_DIR / "netcdf"
PRICE_DIR = DATA_RAW_DIR / "prices"
POWER_CURVE_DIR = DATA_RAW_DIR / "power_curve"
SHAPEFILE_DIR = DATA_DIR / "shapefiles" / "geojson"

# Output data paths
WIND_POWER_DIR = DATA_PROCESSED_DIR / "wind_power"
REGIONS_DIR = DATA_PROCESSED_DIR / "regions"
CAPTURE_PRICE_DIR = DATA_PROCESSED_DIR / "capture_price"
VALUE_FACTOR_DIR = DATA_PROCESSED_DIR / "value_factor"

# Figure output directory
FIGURES_DIR = BASE_DIR / "figures"

# =============================================================================
# DATA PROCESSING PARAMETERS
# =============================================================================

# Price data column names (standardized)
PRICE_TIME_COL = "Datetime (UTC)"
PRICE_VALUE_COL = "Price (EUR/MWhe)"

# Timezone for all temporal data
STANDARD_TIMEZONE = "UTC"

# Missing data handling
MAX_MISSING_HOURS_PER_DAY = 6  # Maximum hours of missing data allowed per day
MAX_INTERPOLATION_GAP = 3  # Maximum consecutive hours for interpolation
