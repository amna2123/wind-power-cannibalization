"""
Compute wind capture price (unit revenue) for zonal regions
using zonal electricity price time series.
"""

import xarray as xr
import pandas as pd
import numpy as np
from pathlib import Path

WIND_DIR = Path("data/processed/regions")
PRICE_DIR = Path("data/raw/prices")
OUTPUT_DIR = Path("data/processed/capture_price_zonal")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

YEARS = range(2015, 2025)

ZONAL_FILES = {
    "SE": "Sweden.csv",
    "IT": "Italy.csv",
    "DK": "Denmark.csv",
    "NO": "Norway.csv",
}

for year in YEARS:
    for f in WIND_DIR.glob(f"wp_*_{year}.nc"):

        zone = f.stem.replace("wp_", "").replace(f"_{year}", "")
        cc = zone.split("_")[0]
        if cc not in ZONAL_FILES:
            continue

        prices = pd.read_csv(PRICE_DIR / ZONAL_FILES[cc])
        prices.columns = prices.columns.str.strip()
        dt = prices.columns[0]
        prices[dt] = pd.to_datetime(prices[dt])
        prices = prices.set_index(dt)
        prices = prices[prices.index.year == year]

        for c in prices.columns:
            prices[c] = pd.to_numeric(prices[c].astype(str).str.replace(",", "."))

        price_col = zone if zone in prices.columns else zone.replace("_", "")
        if price_col not in prices.columns:
            continue

        ds = xr.open_dataset(f).load()
        gen = ds[[v for v in ds.data_vars if v != "spatial_ref"][0]]

        t = pd.to_datetime(ds.time.values).tz_localize("UTC")
        price = prices[price_col].reindex(t, method="nearest")

        ds["price"] = ("time", price.values)
        revenue = gen * ds["price"]

        ds["capture_price"] = revenue.sum("time") / gen.sum("time")
        ds.to_netcdf(OUTPUT_DIR / f"capture_price_{zone}_{year}.nc")
        ds.close()