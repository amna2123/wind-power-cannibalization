"""
Clip gridded wind power NetCDF files by regional GeoJSON polygons.

For each year and each region polygon, the script extracts the
corresponding subset of wind power data and saves it as a NetCDF file.
"""

import xarray as xr
import geopandas as gpd
import rioxarray
from pathlib import Path

INPUT_DIR = Path("data/processed/wind_power")
GEOJSON_DIR = Path("shapefiles/geojson")
OUTPUT_DIR = Path("data/processed/regions")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

YEARS = range(2015, 2025)
CRS = "EPSG:4326"

for year in YEARS:

    nc_file = INPUT_DIR / f"Europe-wind-power-{year}.nc"
    if not nc_file.exists():
        continue

    ds = xr.open_dataset(nc_file)
    var_name = list(ds.data_vars)[0]
    da = ds[var_name]

    lat = next(c for c in da.coords if "lat" in c.lower())
    lon = next(c for c in da.coords if "lon" in c.lower())

    da = da.rio.write_crs(CRS)
    da = da.rio.set_spatial_dims(x_dim=lon, y_dim=lat)

    for geojson in GEOJSON_DIR.glob("*.geojson"):
        region = geojson.stem
        gdf = gpd.read_file(geojson).to_crs(CRS)

        clipped = da.rio.clip(gdf.geometry, gdf.crs, drop=True)
        clipped.to_netcdf(OUTPUT_DIR / f"wp_{region}_{year}.nc")

    ds.close()