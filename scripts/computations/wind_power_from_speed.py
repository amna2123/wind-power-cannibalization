"""
Convert gridded wind speed to wind power using a turbine power curve.

This script transforms hourly wind speed data from ERA5 reanalysis into wind
power generation estimates using a generic turbine power curve. The conversion
is performed through linear interpolation of the power curve at each grid point
and timestep.

The power curve maps wind speed (m/s) to power output (kW) based on typical
characteristics of modern utility-scale wind turbines:
    - Cut-in speed: ~3-4 m/s
    - Rated speed: ~12-15 m/s
    - Cut-out speed: ~25 m/s

Inputs:
    - Hourly wind speed NetCDF files from ERA5 reanalysis
      Location: data/raw/netcdf/
      Format: ERA5_wind_speed_{year}.nc
      Variable: var_100_metre_wind_speed (m/s at 100m height)
      
    - Generic turbine power curve CSV file
      Location: data/raw/power_curve/generic-power-curve.csv
      Format: semicolon-separated, 2 header rows
      Columns: wind_speed (m/s), power_kw (kW)

Outputs:
    - Gridded wind power NetCDF files
      Location: data/processed/wind_power/
      Format: Europe-wind-power-{year}.nc
      Variable: wind_power (kW)

The script processes one year at a time, applying the power curve transformation
to all grid points and timestamps simultaneously using vectorized operations.

Usage:
    python wind_power_from_speed.py

Dependencies:
    - xarray: for NetCDF file handling
    - pandas: for power curve CSV reading
    - numpy: for interpolation and vectorized operations

Notes:
    - Wind speeds outside the power curve range are set to zero output
    - The power curve should represent a typical turbine, not site-specific
    - Results are in absolute power (kW), not capacity factors
    - Processing large NetCDF files may require substantial memory
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
    """
    Convert wind speed to power output using linear interpolation.
    
    Parameters
    ----------
    ws : float or array-like
        Wind speed in m/s
        
    Returns
    -------
    float or array-like
        Power output in kW. Returns 0 for wind speeds below cut-in
        or above cut-out speeds.
    """
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

        # Apply power curve transformation using vectorized operations
        # Note: If data is dask-backed, this will work automatically
        # If memory issues occur, consider chunking the dataset
        wind_power = xr.apply_ufunc(
            interpolate_power_curve,
            wind_speed,
            vectorize=True,
            output_dtypes=[np.float32],
        ).rename("wind_power")

        wind_power.attrs.update({
            "long_name": "Wind power output",
            "units": "kW",
            "description": "Wind power derived from turbine power curve"
        })

        wind_power.to_netcdf(output_file)
