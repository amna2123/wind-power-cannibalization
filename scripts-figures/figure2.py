"""
validation

# ======================================================
# IMPORTS
# ======================================================
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.dates as mdates
from sklearn.linear_model import LinearRegression

# ======================================================
# USER SETTINGS
# ======================================================
DATA_FILE   = "Validation.xlsx"
OBS_SHEET   = "Observed CF"
SIM_SHEET   = "Simulated CF"

YEAR_MIN, YEAR_MAX = 2015, 2019
MAX_CF = 0.95
MAX_SCATTER_POINTS = 20000
N_COLUMNS = 4

OUT_DIR = Path("./figures")
OUT_DIR.mkdir(exist_ok=True)

# ======================================================
# MATPLOTLIB STYLE
# ======================================================
mpl.rcParams.update({
    "font.size": 9,
    "axes.titlesize": 10,
    "axes.labelsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 11,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.3,
})

# ======================================================
# LOAD DATA
# ======================================================
obs = pd.read_excel(
    DATA_FILE, sheet_name=OBS_SHEET,
    parse_dates=["time"]
).set_index("time")

sim = pd.read_excel(
    DATA_FILE, sheet_name=SIM_SHEET,
    index_col=0, parse_dates=True
)

# ---- harmonize time index ----
for df in (obs, sim):
    df.sort_index(inplace=True)
    if df.index.tz is not None:
        df.index = df.index.tz_convert("UTC").tz_localize(None)
    else:
        df.index = df.index.tz_localize(None)

obs.index = obs.index.round("H")
sim.index = sim.index.round("H")

obs = obs[~obs.index.duplicated()]
sim = sim[~sim.index.duplicated()]

# ---- temporal subset ----
mask = lambda df: df[(df.index.year >= YEAR_MIN) & (df.index.year <= YEAR_MAX)]
obs, sim = mask(obs), mask(sim)

# ---- common timestamps ----
idx = obs.index.intersection(sim.index)
obs, sim = obs.loc[idx], sim.loc[idx]

# ---- common countries ----
countries = sorted(set(obs.columns) & set(sim.columns))
if not countries:
    raise ValueError("No overlapping country columns found.")

obs = obs[countries].clip(0, MAX_CF)
sim = sim[countries].clip(0, MAX_CF)

# ======================================================
# HELPERS
# ======================================================
def regression_stats(x, y):
    m = np.isfinite(x) & np.isfinite(y)
    x, y = x[m], y[m]

    if len(x) < 2:
        return dict(R2=np.nan, r=np.nan, MBE=np.nan, RMSE=np.nan,
                    slope=np.nan, intercept=np.nan)

    reg = LinearRegression().fit(x.reshape(-1, 1), y)
    diff = y - x

    return {
        "R2": reg.score(x.reshape(-1, 1), y),
        "r": np.corrcoef(x, y)[0, 1],
        "MBE": np.mean(diff),
        "RMSE": np.sqrt(np.mean(diff**2)),
        "slope": reg.coef_[0],
        "intercept": reg.intercept_,
    }

def add_stats_box(ax, s):
    txt = (
        f"R² = {s['R2']:.2f}\n"
        f"r = {s['r']:.2f}\n"
        f"MBE = {s['MBE']:.2f}\n"
        f"RMSE = {s['RMSE']:.2f}"
    )
    ax.text(
        0.02, 0.98, txt,
        transform=ax.transAxes,
        va="top", ha="left",
        bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="0.5", alpha=0.75)
    )

# ======================================================
# 24h ROLLING MEAN (TIME SERIES)
# ======================================================
obs_24h = obs.rolling("24H", center=True, min_periods=18).mean()
sim_24h = sim.rolling("24H", center=True, min_periods=18).mean()

# ======================================================
# FIGURE LAYOUT
# ======================================================
n = len(countries)
rows = int(np.ceil(n / N_COLUMNS))

fig = plt.figure(figsize=(N_COLUMNS * 3.2, rows * 4.3))
gs = gridspec.GridSpec(
    nrows=rows * 2,
    ncols=N_COLUMNS,
    hspace=0.55,
    wspace=0.25
)

# ======================================================
# (a) TIME SERIES
# ======================================================
axes_a = []

for i, ctry in enumerate(countries):
    r, c = divmod(i, N_COLUMNS)
    ax = fig.add_subplot(gs[r, c])
    axes_a.append(ax)

    ax.plot(sim_24h.index, sim_24h[ctry],
            lw=1.0, color="black", alpha=0.5, label="Simulated")
    ax.plot(obs_24h.index, obs_24h[ctry],
            lw=1.0, color="tab:blue", alpha=0.25, label="Observed")

    ax.set_title(ctry, fontweight="bold")
    ax.set_ylim(0, 1)

    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

    if c == 0:
        ax.set_ylabel("Capacity factor")
    if r == rows - 1:
        ax.set_xlabel("Year")

axes_a[0].text(-0.15, 1.15, "a)", transform=axes_a[0].transAxes,
               fontsize=12, fontweight="bold")

fig.legend(*axes_a[0].get_legend_handles_labels(),
           loc="upper center", ncol=2, frameon=False,
           bbox_to_anchor=(0.5, 0.98))

# ======================================================
# (b) DENSITY SCATTER
# ======================================================
axes_b = []

rng = np.random.RandomState(0)

for i, ctry in enumerate(countries):
    r, c = divmod(i, N_COLUMNS)
    ax = fig.add_subplot(gs[r + rows, c])
    axes_b.append(ax)

    x = obs[ctry].to_numpy()
    y = sim[ctry].to_numpy()

    s = regression_stats(x, y)

    m = np.isfinite(x) & np.isfinite(y)
    x, y = x[m], y[m]

    if len(x) > MAX_SCATTER_POINTS:
        sel = rng.choice(len(x), MAX_SCATTER_POINTS, replace=False)
        x, y = x[sel], y[sel]

    ax.hexbin(x, y, gridsize=60, bins="log", mincnt=1, cmap="viridis")
    ax.plot([0, 1], [0, 1], "k--", lw=1, alpha=0.6)

    if np.isfinite(s["slope"]):
        xx = np.linspace(0, 1, 200)
        ax.plot(xx, s["slope"] * xx + s["intercept"],
                color="black", lw=2.5, alpha=0.35)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title(ctry, fontweight="bold", pad=6)

    add_stats_box(ax, s)

    if c == 0:
        ax.set_ylabel("Simulated CF")
    if r == rows - 1:
        ax.set_xlabel("Observed CF")

axes_b[0].text(-0.15, 1.15, "b)", transform=axes_b[0].transAxes,
               fontsize=12, fontweight="bold")

# ======================================================
# SAVE
# ======================================================
fig.tight_layout(rect=[0, 0, 1, 0.98])
outfile = OUT_DIR / f"onshore_cf_validation_{YEAR_MIN}_{YEAR_MAX}.png"
fig.savefig(outfile, bbox_inches="tight")
plt.show()

print(f"Saved figure to: {outfile.resolve()}")