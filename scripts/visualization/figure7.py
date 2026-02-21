"""
Plot spatial correlation and OLS slope maps between normalized wind potential
and wind value factor over Europe.

Inputs:
- NetCDF file with correlation coefficients
- NetCDF file with OLS regression slopes
- Country-level shapefiles for Europe
"""

import os
import numpy as np
import xarray as xr
import geopandas as gpd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import rioxarray
from scipy.interpolate import griddata
import pandas as pd

# =====================================================
# CONFIGURATION
# =====================================================

CORR_FILE  = "data/value_factor/correlation_2015_2024.nc"
SLOPE_FILE = "data/value_factor/ols_2015_2024.nc"

SHAPEFILE_DIR = "data/shapefiles/europe"
OUTPUT_FIG    = "output.png"

CRS = "EPSG:4326"

LAT_RANGE = (35, 72)
LON_RANGE = (-10, 40)
GRID_RES  = 0.25

COUNTRIES_KEEP = [
    "Spain","Portugal","France","Belgium","Netherlands","Germany","Luxembourg",
    "Switzerland","Austria","Italy","Czech","Slovakia","Hungary","Poland",
    "Slovenia","Romania","Greece","Denmark","Sweden",
    "Norway","Finland","Estonia","Latvia","Lithuania"
]

COUNTRIES_EXCLUDE = ["UK","United_Kingdom","Ireland","Iceland","Cyprus"]

# =====================================================
# LOAD DATA
# =====================================================

corr  = xr.open_dataarray(CORR_FILE).rio.write_crs(CRS)
slope = xr.open_dataarray(SLOPE_FILE).rio.write_crs(CRS)

# =====================================================
# LOAD AND MERGE SHAPEFILES
# =====================================================

gdfs = []

for fname in os.listdir(SHAPEFILE_DIR):
    if not fname.lower().endswith(".shp"):
        continue

    country = fname.replace("_dissolved.shp", "")
    if country not in COUNTRIES_KEEP:
        continue

    gdf = gpd.read_file(os.path.join(SHAPEFILE_DIR, fname))
    gdf["country"] = country
    gdfs.append(gdf)

gdf = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True), crs=gdfs[0].crs)
gdf = gdf.to_crs(CRS)
gdf = gdf[~gdf["country"].isin(COUNTRIES_EXCLUDE)]

europe_geom = gdf.unary_union

# =====================================================
# TARGET GRID
# =====================================================

lat_new = np.arange(LAT_RANGE[0], LAT_RANGE[1] + GRID_RES, GRID_RES)
lon_new = np.arange(LON_RANGE[0], LON_RANGE[1] + GRID_RES, GRID_RES)

def interpolate_and_fill(da):
    """Interpolate to target grid and fill missing values using nearest-neighbor."""
    da_interp = da.interp(latitude=lat_new, longitude=lon_new)

    lon_o, lat_o = np.meshgrid(da.longitude, da.latitude)
    mask = ~np.isnan(da.values)

    points = np.column_stack((lon_o[mask], lat_o[mask]))
    values = da.values[mask]

    lon_g, lat_g = np.meshgrid(lon_new, lat_new)
    target = np.column_stack((lon_g.ravel(), lat_g.ravel()))

    filled = griddata(points, values, target, method="nearest")
    filled = filled.reshape(len(lat_new), len(lon_new))

    return xr.DataArray(
        filled,
        coords={"latitude": lat_new, "longitude": lon_new},
        dims=("latitude", "longitude")
    ).rio.write_crs(CRS)

# =====================================================
# INTERPOLATE AND CLIP
# =====================================================

corr_map  = interpolate_and_fill(corr).rio.clip([europe_geom], CRS, drop=True)
slope_map = interpolate_and_fill(slope).rio.clip([europe_geom], CRS, drop=True)

# =====================================================
# COLOR SCALING
# =====================================================

corr_vmin, corr_vmax = -1, 1
slope_max = np.nanpercentile(np.abs(slope_map), 98)

# =====================================================
# PLOTTING
# =====================================================

fig, axes = plt.subplots(
    1, 2, figsize=(11, 6),
    subplot_kw={"projection": ccrs.PlateCarree()}
)

extent = [*LON_RANGE, *LAT_RANGE]

# (a) Correlation
ax = axes[0]
ax.set_extent(extent)

im0 = corr_map.plot(
    ax=ax,
    cmap="RdBu_r",
    vmin=corr_vmin,
    vmax=corr_vmax,
    add_colorbar=False
)

gdf.boundary.plot(ax=ax, color="black", linewidth=0.6)
ax.set_title("2015–2024", fontsize=11)
ax.text(0.01, 0.98, "a", transform=ax.transAxes,
        fontsize=13, fontweight="bold", va="top")

cbar0 = fig.colorbar(im0, ax=ax, shrink=0.7, pad=0.02)
cbar0.set_label("Correlation")

# (b) OLS slope
ax = axes[1]
ax.set_extent(extent)

im1 = slope_map.plot(
    ax=ax,
    cmap="RdBu_r",
    vmin=-slope_max,
    vmax=slope_max,
    add_colorbar=False
)

gdf.boundary.plot(ax=ax, color="black", linewidth=0.6)
ax.set_title("2015–2024", fontsize=11)
ax.text(0.01, 0.98, "b", transform=ax.transAxes,
        fontsize=13, fontweight="bold", va="top")

cbar1 = fig.colorbar(im1, ax=ax, shrink=0.7, pad=0.02, extend="both")
cbar1.set_label("OLS slope")
cbar1.ax.yaxis.set_major_formatter(
    plt.FuncFormatter(lambda x, _: f"{x:.2f}")
)

# =====================================================
# SAVE
# =====================================================

plt.tight_layout()
plt.savefig(OUTPUT_FIG, dpi=300, bbox_inches="tight")
plt.show()