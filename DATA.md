# Data Requirements and Structure

This document describes the data requirements for reproducing the wind power cannibalization analysis.

## Overview

The analysis requires three primary data sources:
1. Hourly wind speed reanalysis data
2. Hourly electricity price data from European power exchanges
3. Wind turbine power curve specifications
4. Geographic boundary definitions

## Data Directory Structure

```
data/
├── raw/                          # Original, unprocessed input data
│   ├── netcdf/                   # ERA5 wind speed data files
│   ├── prices/                   # Electricity price CSV files
│   └── power_curve/              # Turbine power curve
└── processed/                    # Generated intermediate and final outputs
    ├── wind_power/               # Gridded power generation
    ├── regions/                  # Regional subsets
    ├── capture_price/            # Capture price calculations
    └── value_factor/             # Value factor results
```

## Input Data Specifications

### 1. Wind Speed Data

**Location**: `data/raw/netcdf/`

**Format**: NetCDF (.nc)

**Naming Convention**: `ERA5_wind_speed_{YEAR}.nc`

**Variables Required**:
- Wind speed at 100m height (m/s)
- Time coordinate (hourly resolution, UTC)
- Latitude and longitude coordinates

**Temporal Coverage**: 2015-2024 (10 years)

**Spatial Coverage**: European domain (approximately 35°N-72°N, 12°W-45°E)

**Spatial Resolution**: 0.25° × 0.25° or finer

**Source**: ERA5 reanalysis data from Copernicus Climate Data Store
- Dataset: `reanalysis-era5-single-levels`
- Variable: `100m_u_component_of_wind`, `100m_v_component_of_wind`
- Wind speed magnitude should be calculated from U and V components

**Access**: https://cds.climate.copernicus.eu/

### 2. Electricity Price Data

**Location**: `data/raw/prices/`

**Format**: CSV files

**Naming Convention**: `{CountryName}.csv`

**Required Columns**:
- `Datetime (UTC)`: Timestamp in UTC timezone
- `Price (EUR/MWhe)`: Day-ahead electricity price in EUR per MWh

**Temporal Coverage**: 2015-2024, hourly resolution

**Required Countries**:
- Austria (AT)
- Belgium (BE)
- Bulgaria (BG)
- Switzerland (CH)
- Czech Republic (CZ)
- Germany (DE)
- Estonia (EE)
- Spain (ES)
- Finland (FI)
- France (FR)
- Greece (GR)
- Croatia (HR)
- Hungary (HU)
- Lithuania (LT)
- Latvia (LV)
- Luxembourg (LU)
- Netherlands (NL)
- Poland (PL)
- Portugal (PT)
- Romania (RO)
- Slovenia (SI)
- Slovakia (SK)

**Sources**:
- ENTSO-E Transparency Platform: https://transparency.entsoe.eu/
- Individual power exchange websites (EPEX SPOT, Nord Pool, etc.)

**Notes**: Prices should be day-ahead market clearing prices for the respective bidding zones.

### 3. Wind Turbine Power Curve

**Location**: `data/raw/power_curve/`

**Format**: CSV file

**Filename**: `generic-power-curve.csv`

**Structure**:
- Semicolon-separated values
- Skips first 2 header rows
- Column 1: `wind_speed` (m/s)
- Column 2: `power_kw` (kilowatts)

**Specification**: Generic land-based wind turbine with rated capacity of 2-5 MW, typical cut-in speed of 3-4 m/s, rated wind speed of 12-15 m/s, and cut-out speed of 25 m/s.

**Alternative Sources**:
- Wind turbine manufacturer specifications
- Generic power curves from wind energy literature
- NREL wind turbine database: https://www.nrel.gov/

### 4. Geographic Boundaries

**Location**: `data/shapefiles/geojson/`

**Format**: GeoJSON (.geojson)

**Naming Convention**: `{CountryCode}_{RegionName}.geojson`

**Coordinate Reference System**: EPSG:4326 (WGS84)

**Coverage**: Polygons defining the geographic boundaries of analysis regions within each country. These typically correspond to administrative regions, bidding zones, or aggregated areas of interest.

**Sources**:
- NUTS regions: Eurostat GISCO database
- Bidding zones: ENTSO-E area definitions
- Natural Earth: https://www.naturalearthdata.com/

## Processed Data Outputs

The processing scripts generate intermediate and final outputs in the `data/processed/` directory:

### Wind Power (`data/processed/wind_power/`)
- NetCDF files containing hourly wind power generation (capacity factors)
- Derived from wind speed data and turbine power curve
- Filename: `Europe-wind-power-{YEAR}.nc`

### Regional Extracts (`data/processed/regions/`)
- Regional subsets of wind power data clipped to geographic boundaries
- Filename: `wp_{RegionName}_{YEAR}.nc`

### Capture Price (`data/processed/capture_price/`)
- Wind capture price for each region and year
- Filename: `capture_price_{RegionName}_{YEAR}.nc`

### Value Factor (`data/processed/value_factor/`)
- Value factor calculations (capture price / baseload price)
- Filename: `value_factor_{RegionName}_{YEAR}.nc`

## Data Preparation Notes

### Time Zones
All data must be in UTC timezone to ensure proper alignment between wind generation and electricity prices.

### Missing Data
Handle missing values appropriately:
- Wind speed: Linear interpolation for gaps < 3 hours
- Prices: Use nearest neighbor interpolation for minor gaps
- Discard days with > 6 hours of missing data

### Data Validation
Before running the analysis:
1. Check temporal alignment (all datasets cover 2015-2024)
2. Verify coordinate systems match
3. Confirm price data units (EUR/MWh)
4. Validate wind speed ranges (0-30 m/s typical)

## Storage Requirements

Approximate storage needs:
- Raw wind speed data: ~50-100 GB per year (depends on spatial domain and resolution)
- Price data: ~10-50 MB total
- Processed outputs: ~10-20 GB total
- Generated figures: < 100 MB

## Data Licensing and Citation

Users are responsible for complying with data licenses:
- ERA5: Copernicus License (free for academic and commercial use)
- ENTSO-E: Transparency platform terms of use
- Ensure proper attribution in publications

## Processed Data Availability

The complete processed dataset (wind power generation, capture prices, and value factors for 2015-2024) is available on Zenodo:

**DOI**: [10.5281/zenodo.18733902](https://doi.org/10.5281/zenodo.18733902)

**Title**: Wind Power Cannibalization in Europe - Processed Data

**Authors**: Bibi, Amna; Shafeeque, Muhammad

**Contents**:
- Gridded wind power generation for Europe (2015-2024)
- Regional wind power extracts
- Capture price calculations by country and region
- Value factor time series
- Zonal aggregations for multi-zone countries

This dataset can be used to reproduce the analysis without reprocessing the raw ERA5 data.

## Support

For questions about data preparation or issues with data compatibility, please open an issue on the GitHub repository.
