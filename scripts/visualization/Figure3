"""
Generate Figure 3: Multi-scale plausibility assessment of simulated wind capacity factors.

This script compares simulated, ERA5-based onshore wind capacity factors with
observed or reference capacity-factor series at three spatial scales:

    1. Multi-country aggregate
    2. National
    3. Sub-national or bidding-zone level

The default configuration reproduces a validation design containing:

    - Country-level reference and simulated capacity factors
    - German transmission system operator control areas
    - Swedish electricity bidding zones

Figure panels
-------------
Panel (a)
    Hexbin comparison of observed and simulated multi-country aggregate capacity
    factors, including a 1:1 line, fitted regression line, R-squared, mean bias
    error, and a logarithmic count color scale.

Panel (b)
    Comparison of zone-level R-squared values obtained when each simulated zonal
    series is evaluated against:

        - the matching zonal observation
        - the corresponding national observation
        - the multi-country observed aggregate

Validation metrics
------------------
R²
    Coefficient of determination from an ordinary least-squares regression of
    simulated capacity factor on observed/reference capacity factor.

MBE
    Mean bias error, calculated as simulated minus observed/reference capacity
    factor.

Inputs
------
By default, input files are read from ``data/validation``. Filenames and sheet
names can be changed through command-line options without editing the source
code.

Expected country workbook
    Validation.xlsx

    - Reference sheet: ``ninja_pv_wind_profiles_singlein``
    - Simulated sheet: ``Simulated CF Locations``
    - A time column or datetime index
    - One capacity-factor column per country

Expected German files
    - German_TSO_onshore_wind_CF_2015_2019.csv
    - One observed Excel file for each configured TSO control area

Expected Swedish files
    - Sweden_bidding_zone_onshore_wind_CF_2015_2019.csv
    - One observed CSV file for each configured bidding zone

Outputs
-------
The output directory contains:

    - Figure_3_plausibility_assessment.png
    - Figure_3_plausibility_assessment.pdf
    - Figure_3_panel_a_per_country_r2.csv
    - Figure_3_panel_b_r2_values.csv

Usage
-----
Run with the default repository structure:

    python figure3_plausibility_assessment.py

Specify alternative input and output directories:

    python figure3_plausibility_assessment.py \
        --data-dir path/to/validation_data \
        --output-dir figures

Display all options:

    python figure3_plausibility_assessment.py --help

Dependencies
------------
    - numpy
    - pandas
    - matplotlib
    - scikit-learn
    - openpyxl

Notes
-----
    - All time series are aligned using common timestamps.
    - Duplicate timestamps are averaged.
    - Capacity factors are clipped to a configurable physical range.
    - Swedish local timestamps are converted to UTC when the source time column
      is not explicitly identified as UTC.
    - The multi-country aggregate is capacity-weighted only when complete,
      positive country weights are supplied. Otherwise, equal weighting is used.
    - Statistics are calculated from all overlapping finite observations.
      Optional point subsampling affects only the hexbin visualization.
"""

from __future__ import annotations

import argparse
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D
from matplotlib.ticker import FormatStrFormatter, MultipleLocator
from sklearn.linear_model import LinearRegression

LOGGER = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# DEFAULT DATA CONFIGURATION
# -----------------------------------------------------------------------------

COUNTRY_CODE_TO_NAME = {
    "BE": "Belgium",
    "DK": "Denmark",
    "FI": "Finland",
    "FR": "France",
    "DE": "Germany",
    "NL": "Netherlands",
    "NO": "Norway",
    "SE": "Sweden",
}

GERMANY_ZONES = ("50Hertz", "TenneT", "TransnetBW", "Amprion")
SWEDEN_ZONES = ("SE1", "SE2", "SE3", "SE4")

GERMANY_OBSERVED_FILES = {
    "50Hertz": "50Hertz_onshore_wind_capacity_factor_hourly_2015_2019.xlsx",
    "TenneT": "tennet_onshore_wind_capacity_factor_ratio_REVISED_2015_2019.xlsx",
    "TransnetBW": "transnetbw_onshore_cf_hourly_2015_2019.xlsx",
    "Amprion": "Amprion_onshore_wind_capacity_factor_hourly_2015_2019.xlsx",
}

SWEDEN_OBSERVED_FILES = {
    "SE1": "SE1_hourly_onshore_wind_capacity_factor_2015_2019.csv",
    "SE2": "SE2_hourly_onshore_wind_capacity_factor_2015_2019.csv",
    "SE3": "SE3_hourly_onshore_wind_capacity_factor_2015_2019.csv",
    "SE4": "SE4_hourly_onshore_wind_capacity_factor_2015_2019_CORRECTED.csv",
}

GERMANY_COLUMN_ALIASES = {
    "50hertz": "50Hertz",
    "50HERTZ": "50Hertz",
    "tennet": "TenneT",
    "TENNET": "TenneT",
    "transnetbw": "TransnetBW",
    "TRANSNETBW": "TransnetBW",
    "Transnetbw": "TransnetBW",
    "amprion": "Amprion",
    "AMPRION": "Amprion",
}

ZONE_COLORS = {
    "50Hertz": "#0072B2",
    "TenneT": "#E69F00",
    "TransnetBW": "#009E73",
    "Amprion": "#CC79A7",
    "SE1": "#8C564B",
    "SE2": "#7F7F7F",
    "SE3": "#BCBD22",
    "SE4": "#17BECF",
}

TIME_COLUMN_CANDIDATES = (
    "time_utc",
    "Time UTC",
    "UTC time",
    "utc_time",
    "time",
    "Time",
    "start_time",
    "Start time",
    "Start Time",
    "end_time",
    "End time",
    "End Time",
    "Start date",
    "Start Date",
    "datetime",
    "Datetime",
    "date",
    "Date",
    "timestamp",
    "Timestamp",
)

CF_COLUMN_CANDIDATES = (
    "capacity_factor",
    "Capacity factor",
    "Capacity factor ratio",
    "Hourly CF ratio",
    "CF",
    "cf",
    "Capacity Factor",
)


@dataclass(frozen=True)
class Settings:
    """Runtime settings and repository-relative input paths."""

    data_dir: Path
    output_dir: Path
    country_workbook: str
    reference_sheet: str
    simulated_country_sheet: str
    germany_simulated_file: str
    sweden_simulated_file: str
    year_min: int
    year_max: int
    filter_max: float
    plot_max: float
    max_scatter_points: int | None
    local_timezone_sweden: str
    annotate_r2_values: bool
    capacity_weights_file: Path | None
    show_figure: bool

    @property
    def country_workbook_path(self) -> Path:
        return self.data_dir / self.country_workbook

    @property
    def germany_simulated_path(self) -> Path:
        return self.data_dir / self.germany_simulated_file

    @property
    def sweden_simulated_path(self) -> Path:
        return self.data_dir / self.sweden_simulated_file


@dataclass(frozen=True)
class RegionalGroup:
    """Configuration and data for one group of sub-national zones."""

    country: str
    level_label: str
    zones: tuple[str, ...]
    observed: pd.DataFrame
    simulated: pd.DataFrame


# -----------------------------------------------------------------------------
# COMMAND-LINE INTERFACE
# -----------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Create the multi-scale capacity-factor plausibility-assessment "
            "figure and supporting CSV tables."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data/validation"),
        help="Directory containing all validation input files.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("figures"),
        help="Directory for figures and derived CSV files.",
    )
    parser.add_argument(
        "--country-workbook",
        default="Validation.xlsx",
        help="Excel workbook containing country-level reference and simulated data.",
    )
    parser.add_argument(
        "--reference-sheet",
        default="ninja_pv_wind_profiles_singlein",
        help="Sheet containing country-level observed/reference capacity factors.",
    )
    parser.add_argument(
        "--simulated-country-sheet",
        default="Simulated CF Locations",
        help="Sheet containing country-level simulated capacity factors.",
    )
    parser.add_argument(
        "--germany-simulated-file",
        default="German_TSO_onshore_wind_CF_2015_2019.csv",
        help="CSV containing simulated German TSO control-area capacity factors.",
    )
    parser.add_argument(
        "--sweden-simulated-file",
        default="Sweden_bidding_zone_onshore_wind_CF_2015_2019.csv",
        help="CSV containing simulated Swedish bidding-zone capacity factors.",
    )
    parser.add_argument("--year-min", type=int, default=2015)
    parser.add_argument("--year-max", type=int, default=2019)
    parser.add_argument(
        "--filter-max",
        type=float,
        default=1.0,
        help="Maximum retained capacity factor after clipping.",
    )
    parser.add_argument(
        "--plot-max",
        type=float,
        default=0.99,
        help="Upper plotting threshold for the panel-(a) hexbin only.",
    )
    parser.add_argument(
        "--max-scatter-points",
        type=int,
        default=None,
        help=(
            "Optional maximum number of points displayed in the hexbin. "
            "Statistics always use all valid observations."
        ),
    )
    parser.add_argument(
        "--sweden-timezone",
        default="Europe/Stockholm",
        help="Timezone assumed for Swedish timestamps not explicitly labelled UTC.",
    )
    parser.add_argument(
        "--capacity-weights",
        type=Path,
        default=None,
        help=(
            "Optional CSV with columns 'country' and 'capacity_mw'. The aggregate "
            "uses equal weights when this file is omitted or incomplete."
        ),
    )
    parser.add_argument(
        "--annotate-r2-values",
        action="store_true",
        help="Print numerical R-squared labels above points in panel (b).",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Display the figure interactively after saving it.",
    )
    parser.add_argument(
        "--log-level",
        choices=("DEBUG", "INFO", "WARNING", "ERROR"),
        default="INFO",
    )
    return parser


def settings_from_args(args: argparse.Namespace) -> Settings:
    if args.year_min > args.year_max:
        raise ValueError("--year-min cannot be greater than --year-max.")
    if args.filter_max <= 0:
        raise ValueError("--filter-max must be positive.")
    if not 0 < args.plot_max <= args.filter_max:
        raise ValueError("--plot-max must be positive and no larger than --filter-max.")
    if args.max_scatter_points is not None and args.max_scatter_points < 1:
        raise ValueError("--max-scatter-points must be a positive integer.")

    return Settings(
        data_dir=args.data_dir,
        output_dir=args.output_dir,
        country_workbook=args.country_workbook,
        reference_sheet=args.reference_sheet,
        simulated_country_sheet=args.simulated_country_sheet,
        germany_simulated_file=args.germany_simulated_file,
        sweden_simulated_file=args.sweden_simulated_file,
        year_min=args.year_min,
        year_max=args.year_max,
        filter_max=args.filter_max,
        plot_max=args.plot_max,
        max_scatter_points=args.max_scatter_points,
        local_timezone_sweden=args.sweden_timezone,
        annotate_r2_values=args.annotate_r2_values,
        capacity_weights_file=args.capacity_weights,
        show_figure=args.show,
    )


# -----------------------------------------------------------------------------
# STYLE AND GENERAL HELPERS
# -----------------------------------------------------------------------------


def configure_matplotlib() -> None:
    """Apply publication-oriented Matplotlib defaults."""
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
            "font.size": 8,
            "axes.titlesize": 8,
            "axes.labelsize": 8,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8,
            "figure.dpi": 600,
            "savefig.dpi": 600,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": False,
            "grid.alpha": 0.25,
            "grid.linewidth": 0.35,
        }
    )


def require_file(path: Path, description: str) -> Path:
    """Return a resolved input path or raise a descriptive error."""
    if not path.is_file():
        raise FileNotFoundError(f"Missing {description}: {path}")
    return path


def parse_time_safe(values: object) -> pd.Series | pd.DatetimeIndex:
    """Parse mixed datetime strings while remaining compatible with older pandas."""
    try:
        return pd.to_datetime(values, errors="coerce", format="mixed")
    except (TypeError, ValueError):
        return pd.to_datetime(values, errors="coerce")


def find_column(df: pd.DataFrame, candidates: Sequence[str], variable: str) -> str:
    """Return the first matching column name from a candidate sequence."""
    for column in candidates:
        if column in df.columns:
            return column
    raise ValueError(
        f"No {variable} column found. Available columns: {df.columns.tolist()}"
    )


def find_time_column(df: pd.DataFrame) -> str:
    return find_column(df, TIME_COLUMN_CANDIDATES, "time")


def find_cf_column(df: pd.DataFrame) -> str:
    return find_column(df, CF_COLUMN_CANDIDATES, "capacity-factor")


def to_utc_naive(values: object, assumed_timezone: str | None = None) -> pd.DatetimeIndex:
    """
    Convert timestamps to a UTC-naive DatetimeIndex.

    Naive timestamps are treated as already UTC unless ``assumed_timezone`` is
    supplied. When a timezone is supplied, daylight-saving transitions are
    handled using pandas' inference and forward shifting for nonexistent times.
    """
    parsed = pd.DatetimeIndex(parse_time_safe(values))

    if parsed.tz is not None:
        return parsed.tz_convert("UTC").tz_localize(None)

    if assumed_timezone is not None:
        parsed = parsed.tz_localize(
            assumed_timezone,
            ambiguous="infer",
            nonexistent="shift_forward",
        )
        return parsed.tz_convert("UTC").tz_localize(None)

    return parsed


def clean_time_index(
    df: pd.DataFrame,
    year_min: int,
    year_max: int,
    assumed_timezone: str | None = None,
) -> pd.DataFrame:
    """Normalize, sort, deduplicate, and temporally subset a time-indexed table."""
    cleaned = df.copy()
    cleaned.index = to_utc_naive(cleaned.index, assumed_timezone=assumed_timezone)
    cleaned = cleaned.loc[~cleaned.index.isna()].sort_index()

    if cleaned.index.duplicated().any():
        LOGGER.warning(
            "Averaging %d duplicate timestamps.",
            int(cleaned.index.duplicated().sum()),
        )
        cleaned = cleaned.groupby(level=0).mean(numeric_only=True)

    return cleaned[
        (cleaned.index.year >= year_min) & (cleaned.index.year <= year_max)
    ]


def compute_stats(x: object, y: object) -> tuple[float, float, float, float]:
    """
    Calculate R-squared, MBE, regression slope, and regression intercept.

    ``x`` is the observed/reference capacity factor and ``y`` is the simulated
    capacity factor. MBE is calculated as simulated minus observed/reference.
    """
    x_array = np.asarray(x, dtype=float)
    y_array = np.asarray(y, dtype=float)
    valid = np.isfinite(x_array) & np.isfinite(y_array)
    x_valid = x_array[valid]
    y_valid = y_array[valid]

    if len(x_valid) < 2:
        return np.nan, np.nan, np.nan, np.nan

    regression = LinearRegression().fit(x_valid.reshape(-1, 1), y_valid)
    return (
        float(regression.score(x_valid.reshape(-1, 1), y_valid)),
        float(np.mean(y_valid - x_valid)),
        float(regression.coef_[0]),
        float(regression.intercept_),
    )


def align_xy(
    x_series: pd.Series, y_series: pd.Series
) -> tuple[np.ndarray, np.ndarray]:
    """Inner-join two time-indexed series and return finite paired arrays."""
    paired = pd.concat(
        [x_series.rename("x"), y_series.rename("y")],
        axis=1,
        join="inner",
    ).dropna()
    return (
        paired["x"].to_numpy(dtype=float),
        paired["y"].to_numpy(dtype=float),
    )


def load_capacity_weights(path: Path | None) -> dict[str, float]:
    """Load optional country capacity weights from a two-column CSV file."""
    if path is None:
        return {}

    require_file(path, "capacity-weights CSV")
    table = pd.read_csv(path)
    required = {"country", "capacity_mw"}
    missing = required.difference(table.columns)
    if missing:
        raise ValueError(
            f"Capacity-weights CSV is missing columns {sorted(missing)}: {path}"
        )

    table["capacity_mw"] = pd.to_numeric(table["capacity_mw"], errors="coerce")
    table = table.dropna(subset=["country", "capacity_mw"])
    table = table[table["capacity_mw"] > 0]
    return dict(zip(table["country"].astype(str), table["capacity_mw"].astype(float)))


# -----------------------------------------------------------------------------
# DATA LOADING
# -----------------------------------------------------------------------------


def read_indexed_excel_sheet(path: Path, sheet_name: str) -> pd.DataFrame:
    """Read an Excel sheet and infer its time column or datetime index."""
    table = pd.read_excel(path, sheet_name=sheet_name)
    try:
        time_column = find_time_column(table)
    except ValueError:
        first_column = table.columns[0]
        candidate = parse_time_safe(table[first_column])
        if pd.isna(candidate).all():
            raise ValueError(
                f"No readable time column found in sheet '{sheet_name}' of {path}."
            )
        time_column = first_column

    table[time_column] = parse_time_safe(table[time_column])
    return table.dropna(subset=[time_column]).set_index(time_column)


def load_country_data(settings: Settings) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    """Load, harmonize, and align country-level reference and simulated data."""
    workbook = require_file(settings.country_workbook_path, "country workbook")

    reference = read_indexed_excel_sheet(workbook, settings.reference_sheet)
    simulated = read_indexed_excel_sheet(workbook, settings.simulated_country_sheet)

    reference = clean_time_index(
        reference, settings.year_min, settings.year_max
    )
    simulated = clean_time_index(
        simulated, settings.year_min, settings.year_max
    )

    reference = reference.rename(
        columns={
            column: COUNTRY_CODE_TO_NAME.get(column.split("_")[0], column)
            for column in reference.columns
            if isinstance(column, str)
        }
    )

    common_times = reference.index.intersection(simulated.index)
    if common_times.empty:
        raise ValueError("No common timestamps found in the country-level sheets.")

    reference = reference.loc[common_times]
    simulated = simulated.loc[common_times]

    countries = sorted(set(reference.columns).intersection(simulated.columns))
    if not countries:
        raise ValueError(
            "No common country columns found between the reference and simulated sheets."
        )

    reference = (
        reference[countries]
        .apply(pd.to_numeric, errors="coerce")
        .clip(0, settings.filter_max)
    )
    simulated = (
        simulated[countries]
        .apply(pd.to_numeric, errors="coerce")
        .clip(0, settings.filter_max)
    )

    LOGGER.info("Countries used: %s", ", ".join(countries))
    LOGGER.info("Country reference shape: %s", reference.shape)
    LOGGER.info("Country simulated shape: %s", simulated.shape)
    return reference, simulated, countries


def load_observed_excel_series(
    path: Path,
    zone: str,
    year_min: int,
    year_max: int,
    filter_max: float,
) -> pd.Series:
    """Load one observed zonal capacity-factor series from an Excel workbook."""
    require_file(path, f"observed file for {zone}")
    sheets = pd.read_excel(path, sheet_name=None)

    selected_sheet: str | None = None
    selected_table: pd.DataFrame | None = None
    for sheet_name, table in sheets.items():
        try:
            find_time_column(table)
            find_cf_column(table)
        except ValueError:
            continue
        selected_sheet = sheet_name
        selected_table = table.copy()
        break

    if selected_table is None or selected_sheet is None:
        raise ValueError(f"Could not find time and capacity-factor columns in {path}.")

    time_column = find_time_column(selected_table)
    cf_column = find_cf_column(selected_table)
    LOGGER.info(
        "%s: sheet='%s', time column='%s', CF column='%s'",
        zone,
        selected_sheet,
        time_column,
        cf_column,
    )

    values = pd.to_numeric(selected_table[cf_column], errors="coerce")
    series = pd.Series(
        values.to_numpy(),
        index=parse_time_safe(selected_table[time_column]),
        name=zone,
    )
    frame = clean_time_index(
        series.to_frame(), year_min=year_min, year_max=year_max
    )
    return frame[zone].clip(0, filter_max)


def load_observed_csv_series(
    path: Path,
    zone: str,
    year_min: int,
    year_max: int,
    filter_max: float,
    local_timezone: str | None = None,
) -> pd.Series:
    """Load one observed zonal capacity-factor series from a CSV file."""
    require_file(path, f"observed file for {zone}")
    table = pd.read_csv(path)
    time_column = find_time_column(table)
    cf_column = find_cf_column(table)

    LOGGER.info(
        "%s: time column='%s', CF column='%s'", zone, time_column, cf_column
    )

    timezone = None if "utc" in time_column.lower() else local_timezone
    values = pd.to_numeric(table[cf_column], errors="coerce")
    frame = pd.DataFrame({zone: values.to_numpy()})
    frame.index = to_utc_naive(table[time_column], assumed_timezone=timezone)
    frame = clean_time_index(frame, year_min, year_max)
    return frame[zone].clip(0, filter_max)


def load_simulated_zone_csv(
    path: Path,
    zones: Sequence[str],
    year_min: int,
    year_max: int,
    filter_max: float,
    aliases: Mapping[str, str] | None = None,
) -> pd.DataFrame:
    """Load simulated capacity factors for a configured group of zones."""
    require_file(path, "simulated zonal CSV")
    table = pd.read_csv(path)
    time_column = find_time_column(table)
    table = table.rename(columns=dict(aliases or {}))

    missing_zones = [zone for zone in zones if zone not in table.columns]
    if missing_zones:
        raise ValueError(
            f"Missing simulated zone columns {missing_zones} in {path}. "
            f"Available columns: {table.columns.tolist()}"
        )

    table[time_column] = parse_time_safe(table[time_column])
    table = table.dropna(subset=[time_column]).set_index(time_column)
    table = clean_time_index(table, year_min, year_max)
    return (
        table[list(zones)]
        .apply(pd.to_numeric, errors="coerce")
        .clip(0, filter_max)
    )


def load_regional_groups(settings: Settings) -> list[RegionalGroup]:
    """Load German control-area and Swedish bidding-zone datasets."""
    germany_simulated = load_simulated_zone_csv(
        settings.germany_simulated_path,
        GERMANY_ZONES,
        settings.year_min,
        settings.year_max,
        settings.filter_max,
        aliases=GERMANY_COLUMN_ALIASES,
    )
    germany_observed = pd.concat(
        [
            load_observed_excel_series(
                settings.data_dir / GERMANY_OBSERVED_FILES[zone],
                zone,
                settings.year_min,
                settings.year_max,
                settings.filter_max,
            )
            for zone in GERMANY_ZONES
        ],
        axis=1,
    )
    germany_observed, germany_simulated = germany_observed.align(
        germany_simulated, join="inner", axis=0
    )
    if germany_observed.empty:
        raise ValueError("No common timestamps found for German control areas.")

    sweden_simulated = load_simulated_zone_csv(
        settings.sweden_simulated_path,
        SWEDEN_ZONES,
        settings.year_min,
        settings.year_max,
        settings.filter_max,
    )
    sweden_observed = pd.concat(
        [
            load_observed_csv_series(
                settings.data_dir / SWEDEN_OBSERVED_FILES[zone],
                zone,
                settings.year_min,
                settings.year_max,
                settings.filter_max,
                local_timezone=settings.local_timezone_sweden,
            )
            for zone in SWEDEN_ZONES
        ],
        axis=1,
    )
    sweden_observed, sweden_simulated = sweden_observed.align(
        sweden_simulated, join="inner", axis=0
    )
    if sweden_observed.empty:
        raise ValueError("No common timestamps found for Swedish bidding zones.")

    LOGGER.info("German observed shape: %s", germany_observed.shape)
    LOGGER.info("German simulated shape: %s", germany_simulated.shape)
    LOGGER.info("Swedish observed shape: %s", sweden_observed.shape)
    LOGGER.info("Swedish simulated shape: %s", sweden_simulated.shape)

    return [
        RegionalGroup(
            country="Germany",
            level_label="sub-zonal",
            zones=GERMANY_ZONES,
            observed=germany_observed,
            simulated=germany_simulated,
        ),
        RegionalGroup(
            country="Sweden",
            level_label="zonal",
            zones=SWEDEN_ZONES,
            observed=sweden_observed,
            simulated=sweden_simulated,
        ),
    ]


# -----------------------------------------------------------------------------
# AGGREGATION AND VALIDATION TABLES
# -----------------------------------------------------------------------------


def weighted_multi_country_series(
    table: pd.DataFrame,
    countries: Sequence[str],
    country_capacities: Mapping[str, float],
) -> tuple[pd.Series, str]:
    """
    Aggregate country-level capacity factors at each timestamp.

    Complete positive capacity weights produce a capacity-weighted series.
    Otherwise, the function uses equal country weights and re-normalizes weights
    at timestamps containing missing values.
    """
    weights = np.array(
        [float(country_capacities.get(country, np.nan)) for country in countries],
        dtype=float,
    )

    if np.all(np.isfinite(weights)) and np.sum(weights) > 0:
        weights = weights / np.sum(weights)
        aggregation_mode = "capacity-weighted"
    else:
        weights = np.full(len(countries), 1.0 / len(countries))
        aggregation_mode = "equal-weighted"

    values = table[list(countries)].to_numpy(dtype=float)
    row_weights = weights[np.newaxis, :]
    present = np.isfinite(values)
    available_weight = np.where(present, row_weights, 0.0).sum(axis=1)
    weighted_sum = np.where(present, values * row_weights, 0.0).sum(axis=1)

    output = np.divide(
        weighted_sum,
        available_weight,
        out=np.full(weighted_sum.shape, np.nan, dtype=float),
        where=available_weight > 0,
    )
    return (
        pd.Series(output, index=table.index, name="multi_country_cf"),
        aggregation_mode,
    )


def build_per_country_table(
    reference: pd.DataFrame,
    simulated: pd.DataFrame,
    countries: Sequence[str],
) -> pd.DataFrame:
    """Calculate transparent per-country validation statistics."""
    rows: list[dict[str, float | str | int]] = []
    for country in countries:
        x, y = align_xy(reference[country], simulated[country])
        r2, mbe, slope, intercept = compute_stats(x, y)
        rows.append(
            {
                "country": country,
                "r2": r2,
                "mbe": mbe,
                "slope": slope,
                "intercept": intercept,
                "n": len(x),
            }
        )
    return pd.DataFrame(rows)


def build_scale_comparison_table(
    groups: Sequence[RegionalGroup],
    national_reference: Mapping[str, pd.Series],
    multi_country_reference: pd.Series,
) -> pd.DataFrame:
    """Compare each simulated zone against zonal, national, and aggregate references."""
    rows: list[dict[str, float | str | int]] = []

    for group in groups:
        if group.country not in national_reference:
            raise ValueError(
                f"No national reference series supplied for {group.country}."
            )

        for zone in group.zones:
            x_zonal, y_zonal = align_xy(
                group.observed[zone], group.simulated[zone]
            )
            x_national, y_national = align_xy(
                national_reference[group.country], group.simulated[zone]
            )
            x_multi, y_multi = align_xy(
                multi_country_reference, group.simulated[zone]
            )

            r2_zonal, mbe_zonal, *_ = compute_stats(x_zonal, y_zonal)
            r2_national, mbe_national, *_ = compute_stats(x_national, y_national)
            r2_multi, mbe_multi, *_ = compute_stats(x_multi, y_multi)

            rows.append(
                {
                    "country": group.country,
                    "level_label": group.level_label,
                    "zone": zone,
                    "r2_zonal_vs_zonal": r2_zonal,
                    "r2_zonal_vs_national": r2_national,
                    "r2_zonal_vs_multi_country": r2_multi,
                    "mbe_zonal_vs_zonal": mbe_zonal,
                    "mbe_zonal_vs_national": mbe_national,
                    "mbe_zonal_vs_multi_country": mbe_multi,
                    "n_zonal_vs_zonal": len(x_zonal),
                    "n_zonal_vs_national": len(x_national),
                    "n_zonal_vs_multi_country": len(x_multi),
                }
            )

    return pd.DataFrame(rows)


# -----------------------------------------------------------------------------
# PLOTTING
# -----------------------------------------------------------------------------


def plot_hexbin_panel(
    ax: plt.Axes,
    observed: object,
    simulated: object,
    plot_max: float,
    max_scatter_points: int | None,
) -> tuple[float, float, float, float, mpl.collections.PolyCollection | None]:
    """Plot panel (a) and return its regression statistics and hexbin object."""
    x = np.asarray(observed, dtype=float)
    y = np.asarray(simulated, dtype=float)
    r2, mbe, slope, intercept = compute_stats(x, y)

    valid_plot = (
        np.isfinite(x)
        & np.isfinite(y)
        & (x < plot_max)
        & (y < plot_max)
    )
    x_plot = x[valid_plot]
    y_plot = y[valid_plot]
    n_before_sampling = len(x_plot)

    if max_scatter_points is not None and n_before_sampling > max_scatter_points:
        selection = np.random.default_rng(0).choice(
            n_before_sampling, size=max_scatter_points, replace=False
        )
        x_plot = x_plot[selection]
        y_plot = y_plot[selection]
        LOGGER.info(
            "Hexbin display subsampled from %d to %d points.",
            n_before_sampling,
            max_scatter_points,
        )
    else:
        LOGGER.info("Hexbin display uses all %d valid points.", n_before_sampling)

    hexbin = None
    if len(x_plot) > 0:
        hexbin = ax.hexbin(
            x_plot,
            y_plot,
            gridsize=35,
            cmap="viridis",
            bins="log",
            mincnt=1,
            edgecolors="face",
            linewidths=0.05,
        )

    ax.plot([0, 1], [0, 1], "--", color="0.65", lw=0.75, alpha=0.85, zorder=2)

    if np.isfinite(slope) and np.isfinite(intercept):
        xx = np.linspace(0, 1, 200)
        ax.plot(xx, slope * xx + intercept, color="#B2182B", lw=1.05, zorder=3)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.xaxis.set_major_locator(MultipleLocator(0.5))
    ax.yaxis.set_major_locator(MultipleLocator(0.5))
    ax.xaxis.set_major_formatter(FormatStrFormatter("%.1f"))
    ax.yaxis.set_major_formatter(FormatStrFormatter("%.1f"))
    ax.text(
        0.96,
        0.04,
        f"R² = {r2:.2f}\nMBE = {mbe:.2f}",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=6.5,
        family="monospace",
    )
    ax.tick_params(axis="both", pad=1.5, length=2.5, width=0.5)
    for spine in ax.spines.values():
        spine.set_linewidth(0.5)

    return r2, mbe, slope, intercept, hexbin


def plot_r2_connections(
    ax: plt.Axes,
    r2_table: pd.DataFrame,
    annotate_values: bool,
) -> None:
    """Plot panel (b), grouping legend entries by spatial-level category."""
    x_positions = np.arange(3)
    value_columns = (
        "r2_zonal_vs_zonal",
        "r2_zonal_vs_national",
        "r2_zonal_vs_multi_country",
    )
    labels = (
        "Zonal sim.\nvs zonal obs.",
        "Zonal sim.\nvs national obs.",
        "Zonal sim.\nvs multi-country obs.",
    )
    marker_cycle = ("o", "s", "^", "D")
    group_keys = list(
        dict.fromkeys(
            zip(r2_table["country"], r2_table["level_label"])
        )
    )
    marker_map = {
        key: marker_cycle[index % len(marker_cycle)]
        for index, key in enumerate(group_keys)
    }

    for _, row in r2_table.iterrows():
        zone = str(row["zone"])
        group_key = (str(row["country"]), str(row["level_label"]))
        color = ZONE_COLORS.get(zone, "0.35")
        y_values = row[list(value_columns)].to_numpy(dtype=float)

        ax.plot(
            x_positions,
            y_values,
            color=color,
            lw=1.45,
            marker=marker_map[group_key],
            ms=5.0,
            mfc=color,
            mec="white",
            mew=0.55,
            alpha=0.95,
            label=f"{zone} ({group_key[0]}|{group_key[1]})",
            zorder=3,
        )

        if annotate_values:
            for x_position, value in zip(x_positions, y_values):
                if np.isfinite(value):
                    ax.text(
                        x_position,
                        value + 0.025,
                        f"{value:.2f}",
                        ha="center",
                        va="bottom",
                        fontsize=5.6,
                        color=color,
                    )

    ax.set_xlim(-0.35, 2.35)
    ax.set_ylim(0, 1.0)
    ax.set_xticks(x_positions)
    ax.set_xticklabels(labels)
    ax.set_ylabel("R²")
    ax.yaxis.set_major_locator(MultipleLocator(0.2))
    ax.yaxis.set_major_formatter(FormatStrFormatter("%.1f"))
    ax.grid(axis="y", alpha=0.22, linewidth=0.35)
    ax.tick_params(axis="both", pad=2, length=2.5, width=0.5)
    for spine in ax.spines.values():
        spine.set_linewidth(0.5)

    handles, raw_labels = ax.get_legend_handles_labels()
    blank = Line2D([], [], linestyle="none", marker="", label="")
    legend_handles: list[Line2D] = []
    legend_labels: list[str] = []

    for country, level_label in group_keys:
        token = f"({country}|{level_label})"
        group_items = [
            (handle, label)
            for handle, label in zip(handles, raw_labels)
            if token in label
        ]
        if not group_items:
            continue
        legend_handles.append(blank)
        legend_labels.append(f"{country} ({level_label})")
        for handle, label in group_items:
            legend_handles.append(handle)
            legend_labels.append(label.replace(f" {token}", ""))

    legend = ax.legend(
        legend_handles,
        legend_labels,
        loc="center left",
        bbox_to_anchor=(1.03, 0.50),
        ncol=1,
        frameon=False,
        fontsize=6.4,
        handlelength=1.8,
        handletextpad=0.6,
        borderaxespad=0.0,
    )
    group_headers = {f"{country} ({level})" for country, level in group_keys}
    for text in legend.get_texts():
        if text.get_text() in group_headers:
            text.set_fontweight("bold")
            text.set_fontsize(6.6)


def create_figure(
    observed_multi_country: pd.Series,
    simulated_multi_country: pd.Series,
    r2_table: pd.DataFrame,
    settings: Settings,
) -> plt.Figure:
    """Create the final two-panel publication figure."""
    figure = plt.figure(figsize=(7.20, 3.35), dpi=300)
    grid = GridSpec(
        1,
        2,
        figure=figure,
        width_ratios=[1.0, 1.45],
        wspace=0.35,
        left=0.075,
        right=0.82,
        bottom=0.22,
        top=0.84,
    )

    ax_hexbin = figure.add_subplot(grid[0, 0])
    _, _, _, _, hexbin = plot_hexbin_panel(
        ax_hexbin,
        observed_multi_country.to_numpy(dtype=float),
        simulated_multi_country.to_numpy(dtype=float),
        plot_max=settings.plot_max,
        max_scatter_points=settings.max_scatter_points,
    )
    ax_hexbin.set_xlabel("Observed capacity factor", fontsize=7.5)
    ax_hexbin.set_ylabel("Simulated capacity factor", fontsize=7.5)

    if hexbin is not None:
        colorbar = figure.colorbar(hexbin, ax=ax_hexbin, fraction=0.046, pad=0.04)
        colorbar.set_label("Count", fontsize=7)
        colorbar.ax.yaxis.set_tick_params(which="both", length=0)
        colorbar.ax.tick_params(labelsize=6.5, length=0)
        for tick_line in colorbar.ax.yaxis.get_ticklines():
            tick_line.set_visible(False)
        colorbar.outline.set_linewidth(0.4)

    ax_r2 = figure.add_subplot(grid[0, 1])
    plot_r2_connections(ax_r2, r2_table, settings.annotate_r2_values)

    for axis, label in ((ax_hexbin, "(a)"), (ax_r2, "(b)")):
        axis.text(
            0.03,
            0.97,
            label,
            transform=axis.transAxes,
            ha="left",
            va="top",
            fontsize=8.6,
            fontweight="bold",
        )

    return figure


# -----------------------------------------------------------------------------
# MAIN WORKFLOW
# -----------------------------------------------------------------------------


def run(settings: Settings) -> tuple[Path, Path, Path, Path]:
    """Execute the full analysis and return paths to all generated outputs."""
    configure_matplotlib()
    settings.output_dir.mkdir(parents=True, exist_ok=True)

    capacity_weights = load_capacity_weights(settings.capacity_weights_file)
    reference_country, simulated_country, countries = load_country_data(settings)
    regional_groups = load_regional_groups(settings)

    required_national_series = {group.country for group in regional_groups}
    missing_national = sorted(required_national_series.difference(reference_country.columns))
    if missing_national:
        raise ValueError(
            "Required national reference columns are missing from the country workbook: "
            f"{missing_national}. Available columns: {reference_country.columns.tolist()}"
        )

    observed_multi_country, aggregation_mode = weighted_multi_country_series(
        reference_country, countries, capacity_weights
    )
    simulated_multi_country, _ = weighted_multi_country_series(
        simulated_country, countries, capacity_weights
    )

    aggregate_r2, aggregate_mbe, *_ = compute_stats(
        observed_multi_country.to_numpy(dtype=float),
        simulated_multi_country.to_numpy(dtype=float),
    )
    LOGGER.info("Multi-country aggregation mode: %s", aggregation_mode)
    LOGGER.info("Aggregate R-squared: %.3f", aggregate_r2)
    LOGGER.info("Aggregate MBE: %+.4f", aggregate_mbe)

    per_country_table = build_per_country_table(
        reference_country, simulated_country, countries
    )
    LOGGER.info(
        "Per-country R-squared range: %.3f to %.3f, mean %.3f",
        per_country_table["r2"].min(),
        per_country_table["r2"].max(),
        per_country_table["r2"].mean(),
    )

    national_reference = {
        country: reference_country[country] for country in required_national_series
    }
    r2_table = build_scale_comparison_table(
        regional_groups, national_reference, observed_multi_country
    )

    per_country_path = settings.output_dir / "Figure_3_panel_a_per_country_r2.csv"
    r2_table_path = settings.output_dir / "Figure_3_panel_b_r2_values.csv"
    png_path = settings.output_dir / "Figure_3_plausibility_assessment.png"
    pdf_path = settings.output_dir / "Figure_3_plausibility_assessment.pdf"

    per_country_table.to_csv(per_country_path, index=False)
    r2_table.to_csv(r2_table_path, index=False)

    figure = create_figure(
        observed_multi_country, simulated_multi_country, r2_table, settings
    )
    figure.savefig(png_path, bbox_inches="tight", pad_inches=0.03)
    figure.savefig(pdf_path, bbox_inches="tight", pad_inches=0.03)

    if settings.show_figure:
        plt.show()
    plt.close(figure)

    return png_path, pdf_path, per_country_path, r2_table_path


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(levelname)s: %(message)s",
    )

    try:
        settings = settings_from_args(args)
        outputs = run(settings)
    except (FileNotFoundError, ValueError, KeyError) as error:
        LOGGER.error("%s", error)
        return 1

    LOGGER.info("Saved outputs:")
    for output in outputs:
        LOGGER.info("  %s", output.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
