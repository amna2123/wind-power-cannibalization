# Analysis Workflow

This document describes the recommended workflow for reproducing the wind power cannibalization analysis from raw data to final figures.

## Overview

The analysis consists of two main phases:
1. **Data Processing**: Transform raw data into analysis-ready results
2. **Visualization**: Generate publication figures from processed data

## Prerequisites

Before starting the analysis, ensure:
- All dependencies are installed (`pip install -r requirements.txt`)
- Raw input data is placed in the correct directories (see DATA.md)
- Required directory structure exists (created automatically by scripts)

## Phase 1: Data Processing

Execute the following scripts in order. Each script reads outputs from previous steps.

### Step 1: Convert Wind Speed to Power

```bash
python scripts/computations/wind_power_from_speed.py
```

**Inputs:**
- `data/raw/netcdf/ERA5_wind_speed_{year}.nc` (years 2015-2024)
- `data/raw/power_curve/generic-power-curve.csv`

**Outputs:**
- `data/processed/wind_power/Europe-wind-power-{year}.nc`

**Duration:** ~5-15 minutes per year (depends on domain size)

**Purpose:** Transforms gridded wind speed into wind power potential using a generic turbine power curve.

### Step 2: Extract Regional Subsets

```bash
python scripts/computations/extract_regions.py
```

**Inputs:**
- `data/processed/wind_power/Europe-wind-power-{year}.nc`
- `data/shapefiles/geojson/{region}.geojson`

**Outputs:**
- `data/processed/regions/wp_{region}_{year}.nc`

**Duration:** ~10-60 seconds per region-year combination

**Purpose:** Clips gridded data to regional boundaries for region-specific analysis.

### Step 3: Calculate Capture Price

```bash
python scripts/computations/calculate_capture_price.py
```

**Inputs:**
- `data/processed/regions/wp_{region}_{year}.nc`
- `data/raw/prices/{Country}.csv`

**Outputs:**
- `data/processed/capture_price/capture_price_{region}_{year}.nc`

**Duration:** ~5-20 seconds per region-year

**Purpose:** Computes generation-weighted average electricity prices for each region.

### Step 4: Calculate Value Factor

```bash
python scripts/computations/calculate_value_factor.py
```

**Inputs:**
- `data/processed/regions/wp_{region}_{year}.nc`
- `data/raw/prices/{Country}.csv`

**Outputs:**
- `data/processed/value_factor/value_factor_{region}_{year}.nc`

**Duration:** ~5-20 seconds per region-year

**Purpose:** Computes value factors as the ratio of capture price to baseload price.

### Step 5: Compute Zonal Aggregations (Optional)

For countries with multiple bidding zones:

```bash
python scripts/computations/compute_capture_price_zonal.py
python scripts/computations/compute_value_factor_zonal.py
```

**Purpose:** Aggregates results for countries with zonal electricity markets (Denmark, Italy, Norway, Sweden).

## Phase 2: Figure Generation

Once data processing is complete, generate publication figures. These can be run in any order or in parallel.

### Figure 2: Wind Power Production Potential

```bash
python scripts/visualization/figure2.py
```

**Purpose:** Mean annual wind power generation potential across Europe (2015-2024).

**Output:** `figures/figure2.png`

### Figure 3: Validation

```bash
python scripts/visualization/figure3.py
```

**Purpose:** Validates simulated wind power against observed capacity factors.

**Output:** `figures/figure3.png`

### Figure 4: Spatial Patterns of Capture Price

```bash
python scripts/visualization/figure4.py
```

**Purpose:** Maps spatial distribution of capture price.

**Output:** `figures/figure4.png`

### Figure 5: Value Factor 

```bash
python scripts/visualization/figure5.py
```

**Purpose:** Examines value factors across regions.

**Output:** `figures/figure5.png`

### Figure 6: Quantifying Cannibalization

```bash
python scripts/visualization/figure6.py
```

**Purpose:** Annual evolution of wind value factors and wind generation shares across European countries.

**Output:** `figures/figure6.png`

### Figure 7: Correlation

```bash
python scripts/visualization/figure7.py
```

**Purpose:** Spatial relationship between wind power value factors and wind generation potential.

**Output:** `figures/figure7.png`

## Automation

To run the complete workflow automatically, create a batch script:

**Windows (PowerShell):**
```powershell
# workflow.ps1
$ErrorActionPreference = "Stop"

# Phase 1: Data Processing
Write-Host "Phase 1: Data Processing"
python scripts/computations/wind_power_from_speed.py
python scripts/computations/extract_regions.py
python scripts/computations/calculate_capture_price.py
python scripts/computations/calculate_value_factor.py
python scripts/computations/compute_capture_price_zonal.py
python scripts/computations/compute_value_factor_zonal.py

# Phase 2: Figures
Write-Host "Phase 2: Generating Figures"
python scripts/visualization/figure2.py
python scripts/visualization/figure3.py
python scripts/visualization/figure4.py
python scripts/visualization/figure5.py
python scripts/visualization/figure6.py
python scripts/visualization/figure7.py

Write-Host "Analysis complete!"
```

**Linux/macOS (Bash):**
```bash
#!/bin/bash
set -e

# Phase 1: Data Processing
echo "Phase 1: Data Processing"
python scripts/computations/wind_power_from_speed.py
python scripts/computations/extract_regions.py
python scripts/computations/calculate_capture_price.py
python scripts/computations/calculate_value_factor.py
python scripts/computations/compute_capture_price_zonal.py
python scripts/computations/compute_value_factor_zonal.py

# Phase 2: Figures
echo "Phase 2: Generating Figures"
python scripts/visualization/figure2.py
python scripts/visualization/figure3.py
python scripts/visualization/figure4.py
python scripts/visualization/figure5.py
python scripts/visualization/figure6.py
python scripts/visualization/figure7.py

echo "Analysis complete!"
```

**Using Makefile:**
```bash
make all
```

## Expected Runtime

For the complete 10-year analysis (2015-2024) with ~20 regions:

- **Phase 1 (Data Processing):** 2-4 hours
- **Phase 2 (Figure Generation):** 10-30 minutes
- **Total:** 2.5-4.5 hours

Runtime varies significantly based on:
- Number of regions analyzed
- Size of spatial domain
- Temporal resolution
- Available RAM and CPU cores
- Disk I/O performance

## Storage Requirements

- **Raw data:** ~50-100 GB
- **Processed data:** ~10-20 GB
- **Figures:** < 100 MB
- **Working space:** ~10 GB (for temporary files)
- **Recommended:** 150-200 GB free disk space

## Troubleshooting

### Memory Issues
If scripts crash due to insufficient memory:
- Process fewer years at a time
- Reduce spatial domain size
- Close other applications
- Consider using a machine with more RAM (16+ GB recommended)

### Missing Data
If scripts skip files:
- Check that input filenames match expected patterns
- Verify data is in correct directories
- Check file permissions

### Coordinate Mismatches
If regional extraction fails:
- Verify all data uses EPSG:4326 projection
- Check that latitude/longitude coordinates are correctly specified
- Ensure polygon geometries are valid

### Visualization Errors
If figure generation fails:
- Verify all processed data files exist
- Check that matplotlib backend is properly configured
- Ensure cartopy data files are downloaded

## Partial Reproduction

To reproduce only specific figures without running the full pipeline, ensure the required processed data files are available as specified in each figure script's input requirements.

## Verification

After completing the workflow, verify:
- All expected output files exist
- File sizes are reasonable (not 0 bytes)
- Figures display correctly and contain data
- No error messages in console output

## Contact

For workflow questions or issues, please open an issue on the GitHub repository.
