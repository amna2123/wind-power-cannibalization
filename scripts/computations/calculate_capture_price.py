"""
Calculate wind capture price from hourly generation and electricity prices.

This script computes the capture price (also known as unit revenue) for wind
power generation across multiple European regions and years. The capture price
represents the average electricity price weighted by hourly generation, which
captures the economic value wind power receives in the market.

Capture Price = Sum(Generation_t * Price_t) / Sum(Generation_t)

Inputs:
    - Regional wind power NetCDF files from data/processed/regions/
      Format: wp_{region}_{year}.nc
    - Hourly electricity price CSV files from data/raw/prices/
      Format: {Country}.csv with columns:
        - Datetime (UTC): timestamp in UTC
        - Price (EUR/MWhe): day-ahead market price

Outputs:
    - NetCDF files with capture price for each region and year
      in data/processed/capture_price/
      Format: capture_price_{region}_{year}.nc

The script processes each year and region independently, matching wind generation
timestamps with electricity prices for the corresponding country/bidding zone.

Usage:
    python calculate_capture_price.py

Dependencies:
    - xarray: for NetCDF file handling
    - pandas: for time series operations
    - numpy: for numerical operations

Notes:
    - All timestamps must be in UTC timezone
    - Missing price data is handled by nearest neighbor interpolation
    - Generation data units are assumed to be capacity factors (0-1)
    - Prices are assumed to be in EUR/MWh
"""

import xarray as xr
import pandas as pd
import numpy as np
from pathlib import Path

WIND_DIR = Path("data/processed/regions")
PRICE_DIR = Path("data/raw/prices")
OUTPUT_DIR = Path("data/processed/capture_price")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

YEARS = range(2015, 2025)

PRICE_FILES = {
    "AT": "Austria.csv", "BE": "Belgium.csv", "BG": "Bulgaria.csv",
    "CH": "Switzerland.csv", "CZ": "Czech Republic.csv",
    "EE": "Estonia.csv", "ES": "Spain.csv", "FI": "Finland.csv",
    "FR": "France.csv", "GR": "Greece.csv", "HR": "Croatia.csv",
    "HU": "Hungary.csv", "LT": "Lithuania.csv", "LV": "Latvia.csv",
    "LU": "Luxembourg.csv", "NL": "Netherlands.csv",
    "PL": "Poland.csv", "PT": "Portugal.csv",
    "RO": "Romania.csv", "SI": "Slovenia.csv",
    "SK": "Slovakia.csv", "DE": "Germany.csv",
}

for year in YEARS:
    for f in WIND_DIR.glob(f"wp_*_{year}.nc"):

        region = f.stem.replace("wp_", "").replace(f"_{year}", "")
        cc = region.split("_")[0]
        if cc not in PRICE_FILES:
            continue

        prices = pd.read_csv(PRICE_DIR / PRICE_FILES[cc])
        prices.columns = prices.columns.str.strip()
        prices["Datetime (UTC)"] = pd.to_datetime(prices["Datetime (UTC)"])
        prices = prices.set_index("Datetime (UTC)")
        prices = prices[prices.index.year == year]
        prices["Price (EUR/MWhe)"] = pd.to_numeric(prices["Price (EUR/MWhe)"])

        ds = xr.open_dataset(f).load()
        gen = ds[[v for v in ds.data_vars if v != "spatial_ref"][0]]

        t = pd.to_datetime(ds.time.values).tz_localize("UTC")
        price = prices["Price (EUR/MWhe)"].reindex(t, method="nearest")

        ds["price"] = ("time", price.values)
        revenue = gen * ds["price"]

        ds["capture_price"] = revenue.sum("time") / gen.sum("time")
        ds.to_netcdf(OUTPUT_DIR / f"capture_price_{region}_{year}.nc")
        ds.close()