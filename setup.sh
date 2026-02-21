#!/bin/bash
# Wind Power Cannibalization Analysis - Setup Script
# This script automates the setup process for Unix/Linux/macOS users

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Parse arguments
DEV=false
TEST_IMPORTS=false
HELP=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --dev)
            DEV=true
            shift
            ;;
        --test-imports)
            TEST_IMPORTS=true
            shift
            ;;
        --help|-h)
            HELP=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            HELP=true
            shift
            ;;
    esac
done

if [ "$HELP" = true ]; then
    echo ""
    echo -e "${CYAN}Wind Power Cannibalization Analysis - Setup Script${NC}"
    echo -e "${CYAN}==========================================================${NC}"
    echo ""
    echo -e "${YELLOW}Usage:${NC}"
    echo "  ./setup.sh              Create venv and install dependencies"
    echo "  ./setup.sh --dev        Install development tools too"
    echo "  ./setup.sh --test-imports  Test imports after installation"
    echo "  ./setup.sh --help       Show this help message"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  ./setup.sh              # Basic setup"
    echo "  ./setup.sh --dev        # Dev setup with linting tools"
    echo ""
    exit 0
fi

echo ""
echo -e "${CYAN}Wind Power Cannibalization Analysis - Setup${NC}"
echo -e "${CYAN}=========================================================${NC}"
echo ""

# Check Python version
echo -e "${YELLOW}[1/5] Checking Python version...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo -e "  ${RED}ERROR: Python not found${NC}"
    echo -e "  ${RED}Please install Python 3.10+ from https://www.python.org/${NC}"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
echo -e "  ${GREEN}Found: $PYTHON_VERSION${NC}"

# Extract version numbers
MAJOR_VERSION=$($PYTHON_CMD -c 'import sys; print(sys.version_info.major)')
MINOR_VERSION=$($PYTHON_CMD -c 'import sys; print(sys.version_info.minor)')

if [ "$MAJOR_VERSION" -lt 3 ] || [ "$MAJOR_VERSION" -eq 3 -a "$MINOR_VERSION" -lt 10 ]; then
    echo -e "  ${RED}ERROR: Python 3.10 or higher required${NC}"
    echo -e "  ${RED}Please install Python 3.10+ from https://www.python.org/${NC}"
    exit 1
fi

# Create virtual environment
echo ""
echo -e "${YELLOW}[2/5] Creating virtual environment...${NC}"
if [ -d "venv" ]; then
    echo -e "  ${GREEN}Virtual environment already exists, skipping creation${NC}"
else
    $PYTHON_CMD -m venv venv
    echo -e "  ${GREEN}Virtual environment created successfully${NC}"
fi

# Activate virtual environment
echo ""
echo -e "${YELLOW}[3/5] Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "  ${GREEN}Virtual environment activated${NC}"

# Upgrade pip
echo ""
echo -e "${YELLOW}[4/5] Upgrading pip...${NC}"
pip install --upgrade pip --quiet
echo -e "  ${GREEN}pip upgraded successfully${NC}"

# Install dependencies
echo ""
echo -e "${YELLOW}[5/5] Installing dependencies...${NC}"
if [ "$DEV" = true ]; then
    echo -e "  Installing main dependencies + dev tools..."
    pip install -r requirements.txt --quiet
    pip install ruff black isort pytest pytest-cov --quiet
    echo -e "  ${GREEN}All dependencies installed (including dev tools)${NC}"
else
    echo -e "  Installing main dependencies..."
    pip install -r requirements.txt --quiet
    echo -e "  ${GREEN}All dependencies installed${NC}"
fi

# Test imports if requested
if [ "$TEST_IMPORTS" = true ]; then
    echo ""
    echo -e "${YELLOW}[Bonus] Testing imports...${NC}"

    if python -c "import config" 2>/dev/null; then
        echo -e "  ${GREEN}✓ Config module loaded${NC}"
    fi

    if python -c "import numpy, pandas, xarray" 2>/dev/null; then
        echo -e "  ${GREEN}✓ Data processing libraries OK${NC}"
    fi

    if python -c "import matplotlib, cartopy" 2>/dev/null; then
        echo -e "  ${GREEN}✓ Visualization libraries OK${NC}"
    fi

    if python -c "import geopandas, rioxarray" 2>/dev/null; then
        echo -e "  ${GREEN}✓ Geospatial libraries OK${NC}"
    fi

    echo -e "  ${GREEN}All imports successful!${NC}"
fi

# Success message
echo ""
echo -e "${CYAN}=========================================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${CYAN}=========================================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo "  2. See QUICKSTART.md for data preparation instructions"
echo "  3. See WORKFLOW.md for analysis execution steps"
echo ""
echo -e "${YELLOW}Useful commands:${NC}"
echo "  python scripts/computations/wind_power_from_speed.py"
echo "  python scripts/visualization/figure2.py"
echo ""
echo -e "${YELLOW}Or use Makefile:${NC}"
echo "  make run-computations    # Run all data processing"
echo "  make run-figures         # Generate all figures"
echo "  make all                 # Complete pipeline"
echo ""
