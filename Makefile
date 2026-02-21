.PHONY: help setup install install-dev test test-quick test-coverage lint format clean run-computations run-figures all

help:
	@echo "Wind Power Cannibalization Analysis - Available Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make setup          Create virtual environment"
	@echo "  make install        Install dependencies"
	@echo "  make install-dev    Install dependencies + dev tools"
	@echo ""
	@echo "Testing:"
	@echo "  make test           Run all tests"
	@echo "  make test-quick     Run tests (skip integration tests)"
	@echo "  make test-coverage  Run tests with coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint           Run code quality checks"
	@echo "  make format         Auto-format code"
	@echo ""
	@echo "Analysis:"
	@echo "  make run-computations    Run all data processing scripts"
	@echo "  make run-figures         Generate all figures"
	@echo "  make all                 Run complete analysis pipeline"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean          Remove cache files"
	@echo ""

setup:
	python -m venv venv
	@echo ""
	@echo "Virtual environment created!"
	@echo "Activate it with:"
	@echo "  Windows:  venv\\Scripts\\activate"
	@echo "  Unix:     source venv/bin/activate"
	@echo ""
	@echo "Then run: make install"

install:
	pip install --upgrade pip
	pip install -r requirements.txt
	@echo ""
	@echo "Dependencies installed successfully!"

install-dev:
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install ruff black isort pytest pytest-cov pre-commit
	@echo ""
	@echo "Development environment ready!"

test:
	@echo "Running all tests..."
	@pytest tests/ -v
	@echo "Tests complete!"

test-quick:
	@echo "Running quick tests (skipping integration)..."
	@pytest tests/ -v -m "not integration"
	@echo "Quick tests complete!"

test-coverage:
	@echo "Running tests with coverage..."
	@pytest tests/ -v --cov=. --cov-report=html --cov-report=term
	@echo "Coverage report generated in htmlcov/index.html"

test-imports:
	@echo "Testing core imports..."
	@python -c "import config; print('✓ Config module loaded')"
	@python -c "import numpy, pandas, xarray; print('✓ Data processing libraries OK')"
	@python -c "import matplotlib, cartopy; print('✓ Visualization libraries OK')"
	@python -c "import geopandas, rioxarray; print('✓ Geospatial libraries OK')"
	@echo ""
	@echo "All imports successful!"

lint:
	@echo "Running code quality checks..."
	@ruff check . || true
	@black --check . || true
	@isort --check-only . || true
	@echo "Lint checks complete!"

format:
	@echo "Formatting code..."
	@ruff check --fix .
	@black .
	@isort .
	@echo "Code formatted!"

clean:
	@echo "Cleaning up..."
	@if exist __pycache__ rmdir /s /q __pycache__
	@if exist .pytest_cache rmdir /s /q .pytest_cache
	@if exist .ruff_cache rmdir /s /q .ruff_cache
	@for /d /r %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
	@del /s /q *.pyc 2>nul || true
	@echo "Cleanup complete!"

run-computations:
	@echo "Running data processing pipeline..."
	python scripts/computations/wind_power_from_speed.py
	python scripts/computations/extract_regions.py
	python scripts/computations/calculate_capture_price.py
	python scripts/computations/calculate_value_factor.py
	python scripts/computations/compute_capture_price_zonal.py
	python scripts/computations/compute_value_factor_zonal.py
	@echo "Data processing complete!"

run-figures:
	@echo "Generating figures..."
	python scripts/visualization/figure2.py
	python scripts/visualization/figure3.py
	python scripts/visualization/figure4.py
	python scripts/visualization/figure5.py
	python scripts/visualization/figure6.py
	python scripts/visualization/figure7.py
	@echo "All figures generated!"

all: run-computations run-figures
	@echo ""
	@echo "Complete analysis pipeline finished!"
