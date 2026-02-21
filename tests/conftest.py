"""Pytest configuration and shared fixtures.

This module provides fixtures and configuration for the test suite.
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


@pytest.fixture
def sample_wind_speed_data():
    """Create sample wind speed xarray dataset for testing.

    Returns
    -------
    xr.Dataset
        Sample dataset with wind speed data covering a small European domain
    """
    lats = np.linspace(45, 55, 10)  # Small domain over Central Europe
    lons = np.linspace(5, 15, 10)
    times = pd.date_range("2015-01-01", periods=48, freq="H")

    # Create realistic wind speed data (0-25 m/s)
    np.random.seed(42)
    data = np.random.uniform(0, 25, (len(times), len(lats), len(lons)))

    ds = xr.Dataset(
        {
            "var_100_metre_wind_speed": (["time", "latitude", "longitude"], data)
        },
        coords={
            "time": times,
            "latitude": lats,
            "longitude": lons
        },
        attrs={
            "source": "Test data",
            "units": "m/s"
        }
    )
    return ds


@pytest.fixture
def sample_price_data():
    """Create sample electricity price dataframe for testing.

    Returns
    -------
    pd.DataFrame
        Sample price data with datetime and price columns
    """
    times = pd.date_range("2015-01-01", "2015-12-31 23:00", freq="H")

    # Create realistic price data with daily and seasonal patterns
    np.random.seed(42)
    base_price = 50
    daily_variation = 15 * np.sin(np.arange(len(times)) * 2 * np.pi / 24)
    random_noise = np.random.normal(0, 5, len(times))
    prices = base_price + daily_variation + random_noise
    prices = np.clip(prices, 0, None)  # Ensure non-negative

    df = pd.DataFrame({
        config.PRICE_TIME_COL: times,
        config.PRICE_VALUE_COL: prices
    })
    return df


@pytest.fixture
def sample_power_curve():
    """Create sample power curve data for testing.

    Returns
    -------
    pd.DataFrame
        Sample power curve with wind speed and power output columns
    """
    wind_speeds = [0, 3, 5, 8, 10, 12, 15, 20, 25, 30]
    power_outputs = [0, 0, 200, 600, 1200, 2000, 2000, 2000, 0, 0]

    df = pd.DataFrame({
        "wind_speed": wind_speeds,
        "power_output": power_outputs
    })
    return df


@pytest.fixture
def temp_output_dir(tmp_path):
    """Create temporary output directory for tests.

    Parameters
    ----------
    tmp_path : Path
        Pytest temporary directory fixture

    Returns
    -------
    Path
        Path to temporary output directory
    """
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir
