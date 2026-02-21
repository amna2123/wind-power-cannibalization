"""
Compute wind value factor (VF) for regional NetCDF files.

Value factor is defined as the ratio between the wind capture price
and the annual baseload electricity price.
"""

import xarray as xr
import pandas as pd
import numpy as np
from pathlib import Path

WIND_DIR = Path("data/processed/regions")
PRICE_DIR = Path("data/raw/prices")
OUTPUT_DIR = Path("data/processed/value_factor")
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

        cp = revenue.sum("time") / gen.sum("time")
        baseload = ds["price"].mean("time")

        ds["capture_price"] = cp
        ds["baseload_price"] = baseload
        ds["value_factor"] = cp / baseload

        ds.to_netcdf(OUTPUT_DIR / f"value_factor_{region}_{year}.nc")
        ds.close()