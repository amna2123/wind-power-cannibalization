from pathlib import Path
import numpy as np
import xarray as xr
import geopandas as gpd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import matplotlib.colors as colors
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from matplotlib.gridspec import GridSpec
from shapely.geometry import Point
from shapely.prepared import prep

# ======================================================
# DIRECTORIES
# ======================================================
BASE_DIR = Path(__file__).resolve().parent

DATA_DIR  = BASE_DIR / "data"
CP_DIR    = DATA_DIR / "capture_price"
ANOM_DIR  = DATA_DIR / "anomalies"
SHP_DIR   = BASE_DIR / "shapefiles"
OUT_DIR   = BASE_DIR / "figures"

OUT_DIR.mkdir(exist_ok=True)

# ======================================================
# INPUT FILES
# ======================================================
ANOM_NC  = ANOM_DIR / "capture_price_anomaly_2015_2024.nc"
SHP_FILE = SHP_DIR / "europe.shp"
OUT_FIG  = OUT_DIR / "capture_price_and_anomaly_2015_2024.png"

YEARS  = list(range(2015, 2025))
EXTENT = [-10, 35, 35, 72]
CRS = ccrs.PlateCarree()

# ======================================================
# COLOR SETTINGS
# ======================================================
CP_NORM = colors.Normalize(vmin=10, vmax=220)
ANOM_NORM = colors.TwoSlopeNorm(vmin=-20, vcenter=0, vmax=20)

# ======================================================
# HELPERS
# ======================================================
def detect_lat_lon(da):
    lon = next(c for c in da.coords if c.lower() in ["lon", "longitude", "x"])
    lat = next(c for c in da.coords if c.lower() in ["lat", "latitude", "y"])
    return lon, lat

def to_180(lon):
    return ((lon + 180) % 360) - 180

def countries_with_any_data(gdf, da, lon, lat, stride=6):
    if "time" in da.dims:
        mask2d = np.any(np.isfinite(da.values), axis=0)
    else:
        mask2d = np.isfinite(da.values)

    mask = mask2d[::stride, ::stride]
    if not mask.any():
        return gdf.iloc[0:0]

    lons = da[lon].values[::stride]
    lats = da[lat].values[::stride]

    pts = [
        (float(lons[i]), float(lats[j]))
        for j in range(mask.shape[0])
        for i in range(mask.shape[1])
        if mask[j, i]
    ]

    keep = set()
    for idx, geom in gdf.geometry.items():
        if geom is None or geom.is_empty:
            continue
        pg = prep(geom)
        for x, y in pts:
            if pg.contains(Point(x, y)):
                keep.add(idx)
                break

    return gdf.loc[list(keep)]

# ======================================================
# LOAD SHAPEFILE
# ======================================================
gdf = gpd.read_file(SHP_FILE).to_crs("EPSG:4326")
gdf = gdf[gdf.geometry.notnull() & gdf.geometry.is_valid]

# ======================================================
# LOAD ANOMALY DATA
# ======================================================
ds_anom = xr.open_dataset(ANOM_NC)
da_anom = next(iter(ds_anom.data_vars.values()))

lon_a, lat_a = detect_lat_lon(da_anom)

if da_anom[lon_a].max().item() > 180:
    da_anom = da_anom.assign_coords(
        {lon_a: to_180(da_anom[lon_a])}
    ).sortby(lon_a)

gdf_anom = countries_with_any_data(gdf, da_anom, lon_a, lat_a)

# ======================================================
# FIGURE LAYOUT
# ======================================================
fig = plt.figure(figsize=(14, 10.2), dpi=300)

gs = GridSpec(
    4, 6,
    figure=fig,
    width_ratios=[1, 1, 1, 1, 1, 0.06],
    height_ratios=[1, 1, 1, 1],
    hspace=0.04,
    wspace=0.05
)

axes_cp   = [fig.add_subplot(gs[r, c], projection=CRS) for r in [0, 1] for c in range(5)]
axes_anom = [fig.add_subplot(gs[r, c], projection=CRS) for r in [2, 3] for c in range(5)]

cax_cp   = fig.add_subplot(gs[0:2, 5])
cax_anom = fig.add_subplot(gs[2:4, 5])

# ======================================================
# CAPTURE PRICE PANELS
# ======================================================
mappable_cp = None

for i, year in enumerate(YEARS):
    ax = axes_cp[i]
    fn = CP_DIR / f"merged_capture_price_{year}.nc"

    if not fn.exists():
        ax.axis("off")
        continue

    da = xr.open_dataset(fn)["unit_revenue"]
    lon, lat = detect_lat_lon(da)

    if da[lon].max().item() > 180:
        da = da.assign_coords({lon: to_180(da[lon])}).sortby(lon)

    if da[lat][0].item() < da[lat][-1].item():
        da = da.sortby(lat, ascending=False)

    da = da.sel(**{lon: slice(-10, 35), lat: slice(72, 35)})

    gdf_cp = countries_with_any_data(gdf, da, lon, lat)

    mappable_cp = ax.pcolormesh(
        da[lon], da[lat], da,
        cmap="Spectral_r",
        norm=CP_NORM,
        shading="auto",
        transform=CRS,
        rasterized=True
    )

    gdf_cp.boundary.plot(ax=ax, edgecolor="black", linewidth=0.4, transform=CRS)

    ax.set_extent(EXTENT, CRS)
    ax.text(0.5, 0.98, str(year), transform=ax.transAxes,
            ha="center", va="top", fontsize=10, fontweight="bold")
    ax.set_xticks([])
    ax.set_yticks([])

# ======================================================
# ANOMALY PANELS
# ======================================================
mappable_anom = None

for i, year in enumerate(YEARS):
    ax = axes_anom[i]
    da_y = da_anom.sel(time=year)

    mappable_anom = ax.pcolormesh(
        da_y[lon_a], da_y[lat_a], da_y,
        cmap="coolwarm",
        norm=ANOM_NORM,
        shading="auto",
        transform=CRS
    )

    gdf_anom.boundary.plot(ax=ax, edgecolor="black", linewidth=0.5, transform=CRS)

    ax.set_extent(EXTENT, CRS)
    ax.text(0.5, 0.98, str(year), transform=ax.transAxes,
            ha="center", va="top", fontsize=10, fontweight="bold")
    ax.set_xticks([])
    ax.set_yticks([])

# ======================================================
# COLORBARS
# ======================================================
cb1 = fig.colorbar(mappable_cp, cax=cax_cp, extend="both")
cb1.set_label("Capture Price (EUR/MWh)")
cb1.ax.yaxis.set_major_locator(MultipleLocator(10))
cb1.ax.yaxis.set_major_formatter(FormatStrFormatter("%d"))
cb1.outline.set_visible(False)

cb2 = fig.colorbar(mappable_anom, cax=cax_anom, extend="both")
cb2.set_label("Capture Price Anomaly (EUR/MWh)")
cb2.ax.yaxis.set_major_locator(MultipleLocator(10))
cb2.ax.yaxis.set_major_formatter(FormatStrFormatter("%d"))
cb2.outline.set_visible(False)

fig.text(0.01, 0.955, "(a)", fontsize=14, fontweight="bold")
fig.text(0.01, 0.485, "(b)", fontsize=14, fontweight="bold")

fig.subplots_adjust(left=0.035, right=0.92, top=0.965, bottom=0.06)
fig.savefig(OUT_FIG, dpi=300, pad_inches=0.02)
plt.close(fig)