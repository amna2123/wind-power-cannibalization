from pathlib import Path
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.stats import linregress
from matplotlib.ticker import MaxNLocator

# ======================================================
# PATHS
# ======================================================
BASE_DIR = Path(__file__).resolve().parent
CSV_DIR  = BASE_DIR / "csv"
OUT_DIR  = BASE_DIR / "figures"

OUT_DIR.mkdir(exist_ok=True)

share_csv = CSV_DIR / "generation-onshore-share_2015_2024.csv"
vf_csv    = CSV_DIR / "europe_country_value_factor_stats_2015_2024.csv"
OUTPNG    = OUT_DIR / "out.png"

# ======================================================
# STYLE
# ======================================================
mpl.rcParams.update(mpl.rcParamsDefault)
mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 13,
    "axes.titlesize": 14,
    "xtick.labelsize": 11,
    "ytick.labelsize": 12,
    "legend.fontsize": 13,
    "axes.linewidth": 1.0,
    "xtick.major.width": 0.9,
    "ytick.major.width": 0.9,
    "xtick.major.size": 4,
    "ytick.major.size": 4,
    "grid.linewidth": 0.6,
})

# ======================================================
# CONFIG
# ======================================================
TARGET_CODES = "ES FR DE IT NL BE LU CZ AT PL HU DK SE NO FI PT LT LV EE RO GR".split()

N_COLS = 3
N_ROWS = 7

VF_LW, SHARE_LW = 1.6, 1.6
VF_ALPHA, SH_ALPHA = 0.9, 0.85
vf_color, share_color = "0.2", "tab:green"

code_to_name = {
    "ES":"Spain", "FR":"France", "DE":"Germany", "IT":"Italy", "NL":"Netherlands",
    "BE":"Belgium", "LU":"Luxembourg", "CZ":"Czechia", "AT":"Austria", "PL":"Poland",
    "HU":"Hungary", "DK":"Denmark", "SE":"Sweden", "NO":"Norway", "FI":"Finland",
    "PT":"Portugal", "LT":"Lithuania", "LV":"Latvia", "EE":"Estonia",
    "RO":"Romania", "GR":"Greece"
}

# ======================================================
# LOAD DATA
# ======================================================
share_df = pd.read_csv(share_csv, index_col=0)
vf_df    = pd.read_csv(vf_csv)

share_df.index = pd.to_numeric(share_df.index, errors="coerce")
vf_df["year"]  = pd.to_numeric(vf_df["year"], errors="coerce")

share_df = share_df[share_df.index.notna()]
vf_df    = vf_df[vf_df["year"].notna()]

share_df.index = share_df.index.astype(int)
vf_df["year"]  = vf_df["year"].astype(int)

def build_name_to_code_map():
    m = {
        "hungary": "HU", "czech": "CZ", "czechrepublic": "CZ",
        "czech republic": "CZ", "czechia": "CZ",
        "netherlands": "NL", "the netherlands": "NL",
    }
    for c in TARGET_CODES:
        m[c.lower()] = c
    for c, n in code_to_name.items():
        m[n.lower()] = c
    return m

name_to_code = build_name_to_code_map()

vf_df["country_clean"] = (
    vf_df["country"].astype(str)
    .str.strip().str.lower()
    .str.replace(" ", "")
    .str.replace("-", "")
)

vf_df["_code"] = vf_df["country_clean"].map(name_to_code)
vf_df = vf_df[vf_df["_code"].notna()]

vf_annual = (
    vf_df.assign(avg_vf=pd.to_numeric(vf_df["avg_vf"], errors="coerce"))
    .dropna(subset=["avg_vf"])
    .groupby(["_code", "year"], as_index=False)["avg_vf"]
    .mean()
)

codes = [c for c in TARGET_CODES if c in share_df.columns and c in vf_annual["_code"].values]

# ======================================================
# YEARS
# ======================================================
YEAR_MIN = min(vf_annual["year"].min(), share_df.index.min())
YEAR_MAX = max(vf_annual["year"].max(), share_df.index.max())
ALL_YEARS = np.arange(YEAR_MIN, YEAR_MAX + 1)
XTICKS = np.arange(YEAR_MIN, YEAR_MAX + 1, 2)

def normalize_to_percentage(series):
    s = pd.to_numeric(series, errors="coerce")
    if len(s.dropna()) and s.max() <= 1.0:
        return s * 100
    return s

# ======================================================
# FIGURE
# ======================================================
fig, axes = plt.subplots(
    N_ROWS, N_COLS,
    figsize=(13.5, 1.9 * N_ROWS),
    sharex=True
)
axes = axes.flatten()

l1 = l2 = None
panel_idx = 0

# ======================================================
# MAIN LOOP
# ======================================================
for code in codes:
    ax = axes[panel_idx]
    panel_idx += 1

    s_vf = (
        vf_annual[vf_annual["_code"] == code]
        .set_index("year")["avg_vf"]
        .reindex(ALL_YEARS) * 100
    )

    s_share = normalize_to_percentage(share_df[code].reindex(ALL_YEARS))

    df = pd.DataFrame({"vf": s_vf, "share": s_share})
    df_reg = df.dropna()

    if len(df_reg) >= 3 and df_reg["share"].nunique() > 1:
        res = linregress(df_reg["share"], df_reg["vf"])
        beta = res.slope
        p = res.pvalue
        star = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
        beta_txt = f"β = {beta:.2f}{star}"
    else:
        beta_txt = "β = n/a"

    l1, = ax.plot(df.index, df["vf"], lw=VF_LW, alpha=VF_ALPHA, color=vf_color)
    ax2 = ax.twinx()
    l2, = ax2.plot(df.index, df["share"], lw=SHARE_LW, alpha=SH_ALPHA, color=share_color)

    ax.set_title(code_to_name.get(code, code), fontweight="bold")
    ax.grid(True, alpha=0.25)

    ax.set_ylim(50, 110)
    ax.set_yticks([50, 70, 90, 110])
    ax2.yaxis.set_major_locator(MaxNLocator(5))

    ax.set_xlim(YEAR_MIN - 0.4, YEAR_MAX + 0.4)
    ax.set_xticks(XTICKS)

    ax.text(
        0.03, 0.96, beta_txt,
        transform=ax.transAxes,
        va="top",
        fontsize=12,
        bbox=dict(facecolor="white", alpha=0.85, edgecolor="none")
    )

# ======================================================
# CLEANUP
# ======================================================
for ax in axes[panel_idx:]:
    ax.axis("off")

fig.text(0.02, 0.5, "Value factor (%)", rotation="vertical",
         va="center", fontsize=15, fontweight="bold")

fig.text(0.98, 0.5, "Wind generation share (%)", rotation="vertical",
         va="center", fontsize=15, fontweight="bold", color=share_color)

fig.legend(
    [l1, l2],
    ["Value factor (%)", "Wind generation share (%)"],
    loc="upper center",
    ncol=2,
    frameon=False,
    fontsize=13,
    bbox_to_anchor=(0.5, 0.995)
)

fig.subplots_adjust(
    left=0.075, right=0.925,
    top=0.92, bottom=0.07,
    hspace=0.24, wspace=0.30
)

plt.savefig(OUTPNG, dpi=300, bbox_inches="tight")
plt.show()
print(f"Saved: {OUTPNG}")