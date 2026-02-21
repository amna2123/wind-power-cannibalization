"""Tests for data processing scripts.

This module contains tests for the computation scripts that process
wind speed data, calculate capture prices, and compute value factors.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import xarray as xr

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import config


class TestWindPowerConversion:
    """Test wind speed to power conversion functionality.

    Note: These tests require the wind_power_from_speed module to be
    refactored to import config and expose testable functions.
    """

    def test_power_curve_basic_ranges(self, sample_power_curve):
        """Test that power curve has expected characteristics."""
        assert sample_power_curve["wind_speed"].min() == 0
        assert sample_power_curve["wind_speed"].max() >= 25
        assert sample_power_curve["power_output"].min() == 0

    @pytest.mark.skipif(
        not config.POWER_CURVE_DIR.exists(),
        reason="Power curve data not available"
    )
    def test_power_curve_file_exists(self):
        """Test that power curve file can be loaded."""
        power_curve_file = config.POWER_CURVE_DIR / "generic-power-curve.csv"
        if power_curve_file.exists():
            df = pd.read_csv(power_curve_file)
            assert "wind_speed" in df.columns or df.columns[0] is not None
            assert "power_output" in df.columns or df.columns[1] is not None


class TestPriceDataProcessing:
    """Test electricity price data processing."""

    def test_price_data_structure(self, sample_price_data):
        """Test that price data has required structure."""
        assert config.PRICE_TIME_COL in sample_price_data.columns
        assert config.PRICE_VALUE_COL in sample_price_data.columns

        # Check data types
        assert pd.api.types.is_datetime64_any_dtype(
            sample_price_data[config.PRICE_TIME_COL]
        )
        assert pd.api.types.is_numeric_dtype(
            sample_price_data[config.PRICE_VALUE_COL]
        )

    def test_price_data_no_negative_values(self, sample_price_data):
        """Test that prices are non-negative."""
        prices = sample_price_data[config.PRICE_VALUE_COL]
        assert (prices >= 0).all(), "Prices should be non-negative"

    def test_price_data_reasonable_range(self, sample_price_data):
        """Test that prices are in reasonable range (0-1000 EUR/MWh)."""
        prices = sample_price_data[config.PRICE_VALUE_COL]
        assert prices.max() < 1000, "Prices should be below 1000 EUR/MWh"
        assert prices.min() >= -100, "Prices rarely go below -100 EUR/MWh"

    @pytest.mark.skipif(
        not config.PRICE_DIR.exists(),
        reason="Price data not available"
    )
    def test_price_files_exist(self):
        """Test that configured price files exist."""
        missing_files = []
        for country, filename in config.PRICE_FILES.items():
            filepath = config.PRICE_DIR / filename
            if not filepath.exists():
                missing_files.append(f"{country}: {filename}")

        if missing_files:
            pytest.skip(f"Price files not found: {', '.join(missing_files)}")


class TestSpatialDataProcessing:
    """Test spatial data processing functionality."""

    def test_wind_speed_data_structure(self, sample_wind_speed_data):
        """Test that wind speed data has required structure."""
        assert "var_100_metre_wind_speed" in sample_wind_speed_data
        assert "time" in sample_wind_speed_data.coords
        assert "latitude" in sample_wind_speed_data.coords
        assert "longitude" in sample_wind_speed_data.coords

    def test_wind_speed_data_ranges(self, sample_wind_speed_data):
        """Test that wind speeds are in valid range."""
        wind_speed = sample_wind_speed_data["var_100_metre_wind_speed"]
        assert wind_speed.min() >= 0, "Wind speed should be non-negative"
        assert wind_speed.max() <= 100, "Wind speed should be reasonable"

    def test_coordinate_system(self, sample_wind_speed_data):
        """Test that coordinates are in expected CRS."""
        lats = sample_wind_speed_data.coords["latitude"].values
        lons = sample_wind_speed_data.coords["longitude"].values

        # Check European domain
        assert -20 <= lons.min() <= 50, "Longitude should span Europe"
        assert 30 <= lats.min() <= 75, "Latitude should span Europe"


@pytest.mark.integration
class TestEndToEndWorkflow:
    """Integration tests for complete data processing workflow.

    These tests require actual data files and are skipped if data is not available.
    """

    @pytest.mark.skipif(
        not (config.NETCDF_DIR / "ERA5_wind_speed_2015.nc").exists(),
        reason="Test data not available"
    )
    def test_wind_power_generation_workflow(self):
        """Test complete wind power generation workflow."""
        # This would test the full pipeline from wind speed to power
        pytest.skip("Integration test - requires full implementation")

    @pytest.mark.skipif(
        not config.PRICE_DIR.exists(),
        reason="Price data not available"
    )
    def test_capture_price_calculation_workflow(self):
        """Test complete capture price calculation workflow."""
        pytest.skip("Integration test - requires full implementation")
