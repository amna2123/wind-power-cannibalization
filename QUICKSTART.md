# Quick Start Guide

This guide will help you set up the wind power cannibalization analysis environment quickly.

## Prerequisites

- Python 3.10 or higher installed
- Git installed (for cloning the repository)
- At least 150 GB free disk space (for data storage)
- 8+ GB RAM recommended

## Step 1: Clone the Repository

```bash
git clone https://github.com/amna2123/wind-power-cannibalization.git
cd wind-power-cannibalization
```

## Step 2: Set Up Python Environment

### Option A: Using Makefile (Automated)

```bash
# Create virtual environment
make setup

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On Unix/macOS:
source venv/bin/activate

# Install dependencies
make install
```

### Option B: Manual Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Unix/macOS:
source venv/bin/activate

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

## Step 3: Verify Installation

```bash
# Test that core imports work
make test-imports

# Or manually:
python -c "import config; print('Config OK')"
python -c "import numpy, pandas, xarray; print('Core libraries OK')"
```

**Expected output:**
```
✓ Config module loaded
✓ Data processing libraries OK
✓ Visualization libraries OK
✓ Geospatial libraries OK

All imports successful!
```

## Step 4: Prepare Data

Before running the analysis, you need to obtain the required input data:

1. **Read the data requirements**: See [DATA.md](DATA.md) for detailed specifications
2. **Download ERA5 wind speed data** from Copernicus Climate Data Store
3. **Download electricity price data** from ENTSO-E or individual power exchanges
4. **Obtain wind turbine power curve** (generic curve or specific turbine)
5. **Get geographic boundaries** (GeoJSON format) for your regions of interest

Place data in the following structure:
```
data/
├── raw/
│   ├── netcdf/          # ERA5 wind speed files
│   ├── prices/          # Electricity price CSV files
│   └── power_curve/     # Turbine power curve
└── processed/           # Output (created automatically)
```

## Step 5: Run the Analysis

### Complete Pipeline

Run the entire analysis from start to finish:

```bash
make all
```

This will:
1. Process all wind speed data
2. Extract regional subsets
3. Calculate capture prices
4. Calculate value factors
5. Generate all figures

Expected duration: 2-4 hours depending on your system

### Individual Stages

Alternatively, run stages separately:

**Data Processing:**
```bash
make run-computations
```

**Figure Generation:**
```bash
make run-figures
```

## Step 6: View Results

After running the analysis:
- **Processed data**: `data/processed/` directory
- **Figures**: `figures/` directory (PNG files, 300 DPI)

## Common Issues and Solutions

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'xarray'`

**Solution:**
```bash
# Make sure virtual environment is activated
# Look for (venv) in your terminal prompt
pip install -r requirements.txt
```

### Virtual Environment Not Activating

**Problem:** Virtual environment doesn't activate

**Solution (Windows):**
```powershell
# You may need to allow script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
venv\Scripts\activate
```

**Solution (Unix/macOS):**
```bash
# Make sure the activation script is executable
chmod +x venv/bin/activate
source venv/bin/activate
```

### Cartopy Installation Issues

**Problem:** Cartopy fails to install

**Solution:**
```bash
# On Windows, use conda instead:
conda install -c conda-forge cartopy

# On Unix/macOS:
pip install --upgrade pip setuptools wheel
pip install cartopy
```

### Memory Errors

**Problem:** Scripts crash with `MemoryError`

**Solution:**
- Process fewer years at a time
- Reduce spatial domain size
- Close other applications
- Use a machine with more RAM (16+ GB recommended)

### Missing Data Files

**Problem:** Scripts skip files or report missing data

**Solution:**
- Check file naming matches expected patterns (see DATA.md)
- Verify files are in correct directories
- Check file paths in config.py

## Next Steps

1. **Read the workflow guide**: [WORKFLOW.md](WORKFLOW.md) for detailed execution steps
2. **Understand data requirements**: [DATA.md](DATA.md) for data specifications
3. **Review the code**: Explore scripts in `scripts/computations/` and `scripts/visualization/`

## Getting Help

- **Documentation issues**: Check all .md files in the repository
- **Data questions**: See [DATA.md](DATA.md)
- **Technical problems**: Open an issue on GitHub
- **Contribution guidelines**: See [CONTRIBUTING.md](CONTRIBUTING.md)

## Development Setup

If you plan to modify the code:

```bash
# Install development dependencies
make install-dev

# Run linting before committing
make lint

# Auto-format code
make format
```

## Useful Makefile Commands

View all available commands:
```bash
make help
```

Commands include:
- `make setup` - Create virtual environment
- `make install` - Install dependencies
- `make test-imports` - Test imports
- `make lint` - Run code quality checks
- `make format` - Auto-format code
- `make run-computations` - Run all data processing
- `make run-figures` - Generate all figures
- `make all` - Run complete pipeline
- `make clean` - Remove cache files

## VS Code Users

If you're using Visual Studio Code:
- The repository includes `.vscode/settings.json` with recommended settings
- Python interpreter will automatically point to `venv/`
- Code formatting (Black) and linting (Ruff) are pre-configured
- Simply open the folder in VS Code and select the Python interpreter when prompted

## Success Checklist

- [ ] Repository cloned
- [ ] Virtual environment created and activated
- [ ] Dependencies installed without errors
- [ ] Import tests pass
- [ ] Data downloaded and placed in correct directories
- [ ] First script runs successfully (wind_power_from_speed.py)

Once all items are checked, you're ready to reproduce the full analysis!

## Support

For additional help:
- Review existing [GitHub Issues](https://github.com/amna2123/wind-power-cannibalization/issues)
- Open a new issue with the "Question" template
- Consult the manuscript for methodology details
