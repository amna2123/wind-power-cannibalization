# Wind Power Cannibalization Analysis

This repository contains the computational scripts and analysis code accompanying the research article on wind power cannibalization effects in European electricity markets.

## Overview

This analysis quantifies the cannibalization effect in wind power generation by computing capture prices and value factors across European regions from 2015 to 2024. The study examines how increasing wind power penetration affects the market value of wind-generated electricity through temporal price-supply correlations.

## Documentation

- [QUICKSTART.md](QUICKSTART.md) - Quick setup guide for new users
- [WORKFLOW.md](WORKFLOW.md) - Complete step-by-step analysis workflow
- [DATA.md](DATA.md) - Data requirements, formats, and sources
- [CONTRIBUTING.md](CONTRIBUTING.md) - Guidelines for contributors
- [CITATION.cff](CITATION.cff) - Citation metadata
- [LICENSE](LICENSE) - MIT License

## Repository Structure

```
├── scripts/                   # Analysis scripts
│   ├── computations/          # Data processing pipeline
│   │   ├── wind_power_from_speed.py        # Convert wind speed to power
│   │   ├── extract_regions.py              # Extract regional subsets
│   │   ├── calculate_capture_price.py      # Compute capture prices
│   │   ├── calculate_value_factor.py       # Compute value factors
│   │   ├── compute_capture_price_zonal.py  # Zonal capture prices
│   │   └── compute_value_factor_zonal.py   # Zonal value factors
│   └── visualization/         # Figure generation scripts
│       ├── figure2.py                      # Model validation
│       ├── figure3.py                      # Temporal analysis
│       ├── figure4.py                      # Spatial patterns
│       ├── figure5.py                      # Value factor trends
│       ├── figure6.py                      # Market correlation
│       └── figure7.py                      # Geographic visualization
├── data/                      # Data directory (not in repository)
│   ├── raw/                   # Original input data
│   │   ├── netcdf/            # ERA5 wind speed data
│   │   ├── prices/            # Electricity price data
│   │   └── power_curve/       # Turbine power curve
│   ├── processed/             # Computed outputs
│   │   ├── wind_power/        # Gridded power generation
│   │   ├── regions/           # Regional extracts
│   │   ├── capture_price/     # Capture price results
│   │   └── value_factor/      # Value factor results
│   └── shapefiles/            # Geographic boundaries (not in repository)
│       └── geojson/           # Regional polygon definitions
├── figures/                   # Generated figures (not in repository)
├── .github/                   # GitHub configuration
│   ├── workflows/             # CI/CD pipelines
│   └── ISSUE_TEMPLATE/        # Issue templates
├── .vscode/                   # VS Code configuration
├── config.py                  # Shared configuration constants
├── requirements.txt           # Python dependencies
├── pyproject.toml             # Modern Python project configuration
├── Makefile                   # Automation commands
└── LICENSE                    # MIT License

```

## Data Requirements

This code requires the following input data:

1. **Wind Speed Data**: Hourly ERA5 reanalysis wind speed data (2015-2024) in NetCDF format
2. **Electricity Prices**: Hourly day-ahead electricity prices for European bidding zones (EUR/MWh)
3. **Power Curve**: Generic wind turbine power curve (wind speed to power output mapping)
4. **Geographic Boundaries**: GeoJSON polygons defining regional boundaries

Due to licensing and size constraints, the input data is not included in this repository. See [DATA.md](DATA.md) for detailed data sources and acquisition instructions.

## Installation

### Requirements

- Python 3.10 or higher
- Dependencies listed in requirements.txt

### Quick Setup (Recommended)

**Windows (PowerShell):**
```powershell
.\setup.ps1              # Basic setup
.\setup.ps1 -Dev         # Include development tools
.\setup.ps1 -TestImports # Test imports after setup
```

**Unix/Linux/macOS (Bash):**
```bash
chmod +x setup.sh
./setup.sh               # Basic setup
./setup.sh --dev         # Include development tools
./setup.sh --test-imports # Test imports after setup
```

**Using Makefile:**
```bash
make setup
# Activate virtual environment:
# Windows: venv\Scripts\activate
# Unix: source venv/bin/activate
make install
```

### Manual Setup

Clone the repository:

```bash
git clone https://github.com/amna2123/wind-power-cannibalization.git
cd wind-power-cannibalization
```

Create and activate a virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Unix/macOS:
source venv/bin/activate
```

Install the required Python packages:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Usage

The analysis consists of two main stages: data processing and figure generation. See [WORKFLOW.md](WORKFLOW.md) for the complete step-by-step guide.

### Data Processing

Execute the computation scripts in the following order:

1. Convert wind speed to power output:
   ```bash
   python scripts/computations/wind_power_from_speed.py
   ```

2. Extract regional subsets:
   ```bash
   python scripts/computations/extract_regions.py
   ```

3. Calculate capture prices and value factors:
   ```bash
   python scripts/computations/calculate_capture_price.py
   python scripts/computations/calculate_value_factor.py
   ```

4. Compute zonal aggregations:
   ```bash
   python scripts/computations/compute_capture_price_zonal.py
   python scripts/computations/compute_value_factor_zonal.py
   ```

Or run all computations at once:
```bash
make run-computations
```

### Figure Generation

Generate manuscript figures:

```bash
python scripts/visualization/figure2.py
python scripts/visualization/figure3.py
# ... continue for figures 4-7
```

Or generate all figures at once:
```bash
make run-figures
```

Figures are saved to the `figures/` directory as high-resolution PNG files suitable for publication.

### Complete Pipeline

Run the entire analysis pipeline:
```bash
make all
```

## Testing

A comprehensive test suite is provided to ensure code quality and correctness.

### Running Tests

```bash
# Run all tests
make test

# Run quick tests (skip integration tests)
make test-quick

# Run tests with coverage report
make test-coverage
```

Or use pytest directly:
```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_config.py -v

# Skip integration tests
pytest tests/ -v -m "not integration"
```

### Test Structure

- **tests/test_config.py**: Configuration module tests
- **tests/test_data_processing.py**: Data processing script tests
- **tests/test_visualization.py**: Visualization script tests
- **tests/conftest.py**: Shared test fixtures

## Key Concepts

**Capture Price**: The average electricity price received by wind generators, weighted by their hourly generation. This represents the actual market revenue per unit of energy produced.

**Value Factor (VF)**: The ratio of capture price to the average baseload electricity price. A VF below 1.0 indicates cannibalization, where wind power receives less than the average market price due to supply-demand dynamics.

**Cannibalization Effect**: The reduction in market value of wind-generated electricity as wind penetration increases, caused by the correlation between wind generation patterns and suppressed electricity prices during high-wind periods.

## Citation

If you use this code in your research, please cite:

**Software:**
```bibtex
@software{bibi_shafeeque_2026_windcannibalization,
  author = {Bibi, Amna and Shafeeque, Muhammad},
  title = {Wind Power Cannibalization in Europe},
  year = {2026},
  publisher = {GitHub},
  url = {https://github.com/amna2123/wind-power-cannibalization},
  version = {1.0.0}
}
```

**Processed Data:**
```bibtex
@dataset{bibi_shafeeque_2026_data,
  author = {Bibi, Amna and Shafeeque, Muhammad},
  title = {Wind Power Cannibalization in Europe - Processed Data},
  year = {2026},
  publisher = {Zenodo},
  doi = {10.5281/zenodo.18733902},
  url = {https://doi.org/10.5281/zenodo.18733902}
}
```

See [CITATION.cff](CITATION.cff) for additional citation formats.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Contact

For questions regarding the code or methodology, please open an issue on GitHub or contact the corresponding author listed in the manuscript.

## Contributing

We welcome contributions that improve code quality, fix bugs, or enhance documentation. Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.

## Acknowledgments

This research uses ERA5 reanalysis data provided by the Copernicus Climate Change Service (C3S) and electricity price data from European power exchanges.
