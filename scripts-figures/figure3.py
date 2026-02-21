"""
Mean Wind Power Potential in Europe (2015–2024)
Overlay with onshore wind farm locations
"""

from pathlib import Path
import xarray as xr
import geopandas as gpd
import rioxarray
import matplotlib.pyplot as plt
import pandas as pd

# =====================================================
# PROJECT DIRECTORIES
# =====================================================
BASE_DIR = Path(__file__).resolve().parent

DATA_DIR   = BASE_DIR / "data"
SHAPE_DIR  = BASE_DIR / "shapefiles"
OUTPUT_DIR = BASE_DIR / "figures"

OUTPUT_DIR.mkdir(exist_ok=True)

NETCDF_FILE = DATA_DIR / "input.nc"
EUROPE_SHP  = SHAPE_DIR / "input.shp"
WIND_CSV    = DATA_DIR / "onshore_wind_farms_europe.csv"
OUT_FILE    = OUTPUT_DIR / "output.png"

# =====================================================
# LOAD WIND DATA
# =====================================================
ds = xr.open_dataset(NETCDF_FILE)
wind = ds["var_100_metre_wind_speed"].squeeze()
wind = wind.rename({"longitude": "x", "latitude": "y"})

wind.rio.set_spatial_dims(x_dim="x", y_dim="y", inplace=True)
wind.rio.write_crs("EPSG:4326", inplace=True)

# =====================================================
# LOAD EUROPE SHAPEFILE
# =====================================================
europe = gpd.read_file(EUROPE_SHP).to_crs("EPSG:4326")
europe = europe[europe.is_valid & ~europe.is_empty]

wind_clip = wind.rio.clip(
    europe.geometry.apply(lambda g: g.__geo_interface__),
    europe.crs,
    drop=True
)

# =====================================================
# LOAD WIND FARM LOCATIONS
# =====================================================
df = pd.read_csv(WIND_CSV).dropna(subset=["Longitude", "Latitude"])

wind_farms = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df["Longitude"], df["Latitude"]),
    crs="EPSG:4326"
)

wind_farms = gpd.sjoin(wind_farms, europe, predicate="within")

# =====================================================
# PLOTTING
# =====================================================
fig, ax = plt.subplots(figsize=(10, 8), dpi=300)

img = ax.pcolormesh(
    wind_clip["x"],
    wind_clip["y"],
    wind_clip,
    cmap="RdYlBu_r",
    vmin=100,
    vmax=1200,
    shading="auto"
)

europe.boundary.plot(ax=ax, color="black", linewidth=0.5)

ax.scatter(
    wind_farms["Longitude"],
    wind_farms["Latitude"],
    s=5,
    facecolors="none",
    edgecolors="green",
    linewidth=0.4,
    alpha=0.7,
    label="Wind farms"
)

cbar = plt.colorbar(img, ax=ax, shrink=0.75, pad=0.02)
cbar.set_label("Mean wind power potential (kW)")

ax.set_title("Mean Wind Power Potential in Europe (2015–2024)", fontsize=11)
ax.set_xlim(-10, 45)
ax.set_ylim(34, 72)
ax.legend(loc="lower left", fontsize=8)
ax.grid(alpha=0.3)

fig.tight_layout()
fig.savefig(OUT_FILE, dpi=600, bbox_inches="tight")
plt.show()