"""
Extract regional subsets from gridded wind power data using spatial boundaries.

This script clips gridded wind power NetCDF files to specific geographic regions
defined by GeoJSON polygon boundaries. Each region is processed separately,
creating individual NetCDF files containing only the data within the specified
geographic extent.

This spatial subsetting is necessary to:
    1. Match wind generation data with regional electricity prices
    2. Align with administrative or market boundaries (bidding zones)
    3. Reduce file sizes for region-specific analysis
    4. Enable parallel processing of different regions

Inputs:
    - Gridded wind power NetCDF files for Europe
      Location: data/processed/wind_power/
      Format: Europe-wind-power-{year}.nc
      Contains: 3D array of wind power [time, lat, lon]

    - Regional boundary GeoJSON files
      Location: data/shapefiles/geojson/
      Format: {RegionName}.geojson
      CRS: EPSG:4326 (WGS84)
      One or more polygons defining the region extent

Outputs:
    - Regional wind power NetCDF files
      Location: data/processed/regions/
      Format: wp_{region}_{year}.nc
      Contains: Wind power data clipped to region boundaries

The script processes all years and all available GeoJSON regions, creating a
separate output file for each year-region combination.

Usage:
    python extract_regions.py

Dependencies:
    - xarray: for NetCDF file handling
    - geopandas: for reading and processing GeoJSON boundaries
    - rioxarray: for spatial operations and clipping

Technical Notes:
    - Uses rioxarray for efficient spatial clipping
    - Preserves all original data attributes and metadata
    - Automatically detects latitude and longitude coordinate names
    - Handles multi-polygon geometries correctly
    - Grid cells are included if their center falls within the polygon
    - CRS must match between NetCDF and GeoJSON (EPSG:4326)

Performance:
    - Processing time depends on region size and temporal resolution
    - Typical runtime: 10-60 seconds per region-year combination
    - Memory requirements: ~1-2 GB per year of data
"""

from pathlib import Path

import geopandas as gpd
import rioxarray
import xarray as xr

INPUT_DIR = Path("data/processed/wind_power")
GEOJSON_DIR = Path("data/shapefiles/geojson")
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
