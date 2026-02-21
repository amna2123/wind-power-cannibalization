from pathlib import Path

import cartopy.crs as ccrs
import geopandas as gpd
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from matplotlib.lines import Line2D
from matplotlib.ticker import FormatStrFormatter
from scipy.stats import linregress

# ======================================================
# PATHS
# ======================================================
BASE_DIR = Path(__file__).resolve().parent

DATA_DIR   = BASE_DIR / "data" / "value_factor"
SHAPE_DIR  = BASE_DIR / "data" / "shapefiles" / "countries"
OUT_DIR    = BASE_DIR / "figures"

OUT_DIR.mkdir(exist_ok=True)

# ======================================================
# SETTINGS
# ======================================================
YEARS = list(range(2015, 2025))

EXTENT = [-10, 35, 35, 72]
CRS = ccrs.PlateCarree()

VF_NORM = colors.Normalize(vmin=0.4, vmax=1.4)
TREND_NORM = colors.TwoSlopeNorm(vmin=-0.10, vcenter=0, vmax=0.10)

VF_CMAP = "PuOr"
TREND_CMAP = "RdBu_r"

# ======================================================
# LOAD & SIMPLIFY BORDERS
# ======================================================
country_files = [
    "Spain.shp", "France.shp", "Germany.shp", "Italy.shp",
    "Netherlands.shp", "Belgium.shp", "Luxembourg.shp",
    "Switzerland.shp", "Czech.shp", "Austria.shp",
    "Poland.shp", "Slovakia.shp", "Hungary.shp",
    "Denmark.shp", "Sweden.shp", "Norway.shp",
    "Finland.shp", "Portugal.shp", "Lithuania.shp",
    "Latvia.shp", "Estonia.shp", "Romania.shp",
    "Greece.shp", "Slovenia.shp",
]

borders = []
for shp in country_files:
    p = SHAPE_DIR / shp
    if p.exists():
        g = gpd.read_file(p).to_crs("EPSG:4326")
        g.geometry = g.geometry.simplify(0.01, preserve_topology=True)
        borders.append(g.boundary)

def plot_borders(ax):
    for b in borders:
        b.plot(ax=ax, edgecolor="black", linewidth=0.4, transform=CRS)

# ======================================================
# LOAD DATA
# ======================================================
def load_all_years(years):
    das = []
    for y in years:
        fn = DATA_DIR / f"value_factor_merged_{y}.nc"
        da = xr.open_dataarray(fn).expand_dims(time=[y])
        if "latitude" in da.dims:
            da = da.rename({"latitude": "lat", "longitude": "lon"})
        das.append(da)
    return xr.concat(das, dim="time")

def compute_trend_and_pvalue(da):
    years = da["time"].values.astype(float)

    def _regress(y):
        m = np.isfinite(y)
        if m.sum() < 5:
            return np.nan, np.nan
        r = linregress(years[m], y[m])
        return r.slope, r.pvalue

    return xr.apply_ufunc(
        _regress,
        da,
        input_core_dims=[["time"]],
        output_core_dims=[[], []],
        vectorize=True,
        output_dtypes=[float, float],
    )

vf_all = load_all_years(YEARS)
vf_trend, vf_p = compute_trend_and_pvalue(vf_all)

mask = ~np.isnan(vf_all.isel(time=0))
vf_trend = vf_trend.where(mask)
vf_p = vf_p.where(mask)

lon = vf_trend.lon
lat = vf_trend.lat

# ======================================================
# FIGURE
# ======================================================
fig = plt.figure(figsize=(16, 10), dpi=300)

gs = fig.add_gridspec(
    nrows=3, ncols=4,
    left=0.04, right=0.94,
    top=0.95, bottom=0.06,
    hspace=0.04, wspace=0.02
)

# ======================================================
# (a) ANNUAL VALUE FACTOR MAPS
# ======================================================
for i, year in enumerate(YEARS):
    ax = fig.add_subplot(gs[i // 4, i % 4], projection=CRS)

    da = xr.open_dataarray(DATA_DIR / f"value_factor_average_{year}.nc")
    if "latitude" in da.dims:
        da = da.rename({"latitude": "lat", "longitude": "lon"})

    im_vf = ax.pcolormesh(
        da.lon, da.lat, da,
        cmap=VF_CMAP,
        norm=VF_NORM,
        shading="auto",
        transform=CRS,
        rasterized=True
    )

    plot_borders(ax)
    ax.set_extent(EXTENT, CRS)
    ax.set_aspect("auto")

    ax.text(
        0.5, 0.98, str(year),
        transform=ax.transAxes,
        ha="center", va="top",
        fontsize=11, fontweight="bold"
    )

    ax.set_xticks([])
    ax.set_yticks([])

fig.text(0.02, 0.93, "(a)", fontsize=14, fontweight="bold")

cax_vf = fig.add_axes([0.955, 0.38, 0.012, 0.54])
cb_vf = fig.colorbar(im_vf, cax=cax_vf, extend="both")
cb_vf.set_label("Value Factor", fontsize=11)
cb_vf.outline.set_visible(False)

# ======================================================
# (b) TREND MAP
# ======================================================
ax_trend = fig.add_subplot(gs[2, 2], projection=CRS)

im_trend = ax_trend.pcolormesh(
    lon, lat, vf_trend,
    cmap=TREND_CMAP,
    norm=TREND_NORM,
    shading="auto",
    transform=CRS,
    rasterized=True
)

sig = vf_p < 0.05
LON, LAT = np.meshgrid(lon.values, lat.values)

ax_trend.scatter(
    LON[sig.values],
    LAT[sig.values],
    s=4,
    c="k",
    marker=".",
    linewidths=0,
    transform=CRS
)

plot_borders(ax_trend)
ax_trend.set_extent(EXTENT, CRS)
ax_trend.set_aspect("auto")
ax_trend.set_xticks([])
ax_trend.set_yticks([])

fig.text(0.50, 0.32, "(b) Trend", fontsize=14, fontweight="bold")

cax_trend = fig.add_axes([0.745, 0.06, 0.012, 0.28])
cb_trend = fig.colorbar(im_trend, cax=cax_trend, extend="both")
cb_trend.set_label("Value Factor yr⁻¹", fontsize=11)
cb_trend.ax.yaxis.set_major_formatter(FormatStrFormatter("%.2f"))
cb_trend.outline.set_visible(False)

legend_elements = [
    Line2D([0], [0], marker=".", color="k", lw=0, markersize=6, label="p < 0.05")
]
ax_trend.legend(handles=legend_elements, loc="upper right", fontsize=9, frameon=True)

# ======================================================
# SAVE
# ======================================================
out = OUT_DIR / "VF_Europe_2015_2024_with_trend.png"
fig.savefig(out, dpi=300, bbox_inches="tight", pad_inches=0.05)
plt.close(fig)
