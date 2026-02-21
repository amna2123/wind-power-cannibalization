# Wind Power Cannibalization Analysis - Setup Script
# This script automates the setup process for Windows users

param(
    [switch]$Dev,
    [switch]$TestImports,
    [switch]$Help
)

$ErrorActionPreference = "Stop"

function Show-Help {
    Write-Host ""
    Write-Host "Wind Power Cannibalization Analysis - Setup Script" -ForegroundColor Cyan
    Write-Host "==========================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\setup.ps1              Create venv and install dependencies"
    Write-Host "  .\setup.ps1 -Dev         Install development tools too"
    Write-Host "  .\setup.ps1 -TestImports Test imports after installation"
    Write-Host "  .\setup.ps1 -Help        Show this help message"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\setup.ps1              # Basic setup"
    Write-Host "  .\setup.ps1 -Dev         # Dev setup with linting tools"
    Write-Host ""
}

if ($Help) {
    Show-Help
    exit 0
}

Write-Host ""
Write-Host "Wind Power Cannibalization Analysis - Setup" -ForegroundColor Cyan
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "[1/5] Checking Python version..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  Found: $pythonVersion" -ForegroundColor Green

    # Extract version number
    $versionMatch = $pythonVersion -match "Python (\d+)\.(\d+)"
    if ($versionMatch) {
        $major = [int]$Matches[1]
        $minor = [int]$Matches[2]

        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 10)) {
            Write-Host "  ERROR: Python 3.10 or higher required" -ForegroundColor Red
            Write-Host "  Please install Python 3.10+ from https://www.python.org/" -ForegroundColor Red
            exit 1
        }
    }
} catch {
    Write-Host "  ERROR: Python not found in PATH" -ForegroundColor Red
    Write-Host "  Please install Python 3.10+ from https://www.python.org/" -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host ""
Write-Host "[2/5] Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "  Virtual environment already exists, skipping creation" -ForegroundColor Gray
} else {
    python -m venv venv
    Write-Host "  Virtual environment created successfully" -ForegroundColor Green
}

# Activate virtual environment
Write-Host ""
Write-Host "[3/5] Activating virtual environment..." -ForegroundColor Yellow
$activateScript = "venv\Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    . $activateScript
    Write-Host "  Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "  ERROR: Could not find activation script" -ForegroundColor Red
    exit 1
}

# Upgrade pip
Write-Host ""
Write-Host "[4/5] Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
Write-Host "  pip upgraded successfully" -ForegroundColor Green

# Install dependencies
Write-Host ""
Write-Host "[5/5] Installing dependencies..." -ForegroundColor Yellow
if ($Dev) {
    Write-Host "  Installing main dependencies + dev tools..." -ForegroundColor Gray
    pip install -r requirements.txt --quiet
    pip install ruff black isort pytest pytest-cov --quiet
    Write-Host "  All dependencies installed (including dev tools)" -ForegroundColor Green
} else {
    Write-Host "  Installing main dependencies..." -ForegroundColor Gray
    pip install -r requirements.txt --quiet
    Write-Host "  All dependencies installed" -ForegroundColor Green
}

# Test imports if requested
if ($TestImports) {
    Write-Host ""
    Write-Host "[Bonus] Testing imports..." -ForegroundColor Yellow

    try {
        python -c "import config; print('  ✓ Config module loaded')"
        python -c "import numpy, pandas, xarray; print('  ✓ Data processing libraries OK')"
        python -c "import matplotlib, cartopy; print('  ✓ Visualization libraries OK')"
        python -c "import geopandas, rioxarray; print('  ✓ Geospatial libraries OK')"
        Write-Host "  All imports successful!" -ForegroundColor Green
    } catch {
        Write-Host "  WARNING: Some imports failed" -ForegroundColor Red
        Write-Host "  This might be normal if data files are missing" -ForegroundColor Gray
    }
}

# Success message
Write-Host ""
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Keep the virtual environment activated in this terminal"
Write-Host "  2. See QUICKSTART.md for data preparation instructions"
Write-Host "  3. See WORKFLOW.md for analysis execution steps"
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Yellow
Write-Host "  python scripts/computations/wind_power_from_speed.py"
Write-Host "  python scripts/visualization/figure2.py"
Write-Host ""
Write-Host "To activate this environment in future sessions:" -ForegroundColor Yellow
Write-Host "  venv\Scripts\Activate.ps1"
Write-Host ""
Write-Host "If you encounter script execution issues, run:" -ForegroundColor Yellow
Write-Host "  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser"
Write-Host ""
