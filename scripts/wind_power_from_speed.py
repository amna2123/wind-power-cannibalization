"""
Convert gridded wind speed to wind power using a turbine power curve.

The script interpolates a turbine power curve to hourly wind speed data
and produces a gridded wind power NetCDF file suitable for further
spatial and economic analysis.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import xarray as xr

# =================================================
# CONFIGURATION
# =================================================
BASE_DIR = Path(__file__).resolve().parents[1]

POWER_CURVE_FILE = BASE_DIR / "data/raw/power_curve/generic-power-curve.csv"
INPUT_DIR = BASE_DIR / "data/raw/netcdf"
OUTPUT_DIR = BASE_DIR / "data/processed/wind_power"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

YEARS = range(2015, 2025)

# =================================================
# LOAD POWER CURVE
# =================================================
pc = pd.read_csv(
    POWER_CURVE_FILE, skiprows=2, sep=";" ,names=["wind_speed", "power_kw"]
)

pc["wind_speed"] = pd.to_numeric(pc["wind_speed"], errors="coerce")
pc["power_kw"] = pd.to_numeric(pc["power_kw"], errors="coerce")
pc = pc.dropna().sort_values("wind_speed")

wind_speeds = pc["wind_speed"].values
power_output = pc["power_kw"].values


def interpolate_power_curve(ws):
    return np.interp(ws, wind_speeds, power_output, left=0.0, right=0.0)


# =================================================
# LOOP OVER YEARS
# =================================================
for year in YEARS:

    input_file = INPUT_DIR / f"ERA5_wind_speed_{year}.nc"
    output_file = OUTPUT_DIR / f"Europe-wind-power-{year}.nc"

    if not input_file.exists():
        continue

    with xr.open_dataset(input_file) as ds:
        wind_speed = ds["var_100_metre_wind_speed"]

        wind_power = xr.apply_ufunc(
            interpolate_power_curve,
            wind_speed,
            vectorize=True,
            dask="parallelized",
            output_dtypes=[np.float32],
        ).rename("wind_power")

        wind_power.attrs.update({
            "long_name": "Wind power output",
            "units": "kW"
        })

        wind_power.to_netcdf(output_file)