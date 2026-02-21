"""Tests for configuration module.

This module tests that config.py contains all required constants
and that values are valid.
"""

import sys
from pathlib import Path

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import config


class TestConfigConstants:
    """Test configuration constants are defined and valid."""

    def test_years_configuration(self):
        """Test that year configuration is valid."""
        assert hasattr(config, 'START_YEAR')
        assert hasattr(config, 'END_YEAR')
        assert hasattr(config, 'YEARS')
        assert config.START_YEAR >= 2000
        assert config.END_YEAR >= config.START_YEAR
        assert len(list(config.YEARS)) > 0

    def test_price_files_mapping(self):
        """Test that price file mappings are complete."""
        assert hasattr(config, 'PRICE_FILES')
        assert isinstance(config.PRICE_FILES, dict)
        assert len(config.PRICE_FILES) > 0

        # Check all values end with .csv
        for country, filename in config.PRICE_FILES.items():
            assert filename.endswith('.csv'), f"{country} file should be CSV"
            assert len(country) == 2, f"Country code should be 2 letters: {country}"

    def test_zonal_files_mapping(self):
        """Test that zonal file mappings are defined."""
        assert hasattr(config, 'ZONAL_FILES')
        assert isinstance(config.ZONAL_FILES, dict)
        assert len(config.ZONAL_FILES) > 0

    def test_spatial_configuration(self):
        """Test spatial configuration constants."""
        assert hasattr(config, 'DEFAULT_CRS')
        assert config.DEFAULT_CRS == "EPSG:4326"

        assert hasattr(config, 'EUROPE_EXTENT')
        assert len(config.EUROPE_EXTENT) == 4

    def test_wind_power_constants(self):
        """Test wind power conversion constants."""
        assert hasattr(config, 'MIN_WIND_SPEED')
        assert hasattr(config, 'MAX_WIND_SPEED')
        assert config.MIN_WIND_SPEED >= 0
        assert config.MAX_WIND_SPEED > config.MIN_WIND_SPEED

        assert hasattr(config, 'MAX_CAPACITY_FACTOR')
        assert 0 < config.MAX_CAPACITY_FACTOR <= 1.0

        assert hasattr(config, 'DEFAULT_CUT_IN_SPEED')
        assert hasattr(config, 'DEFAULT_RATED_SPEED')
        assert hasattr(config, 'DEFAULT_CUT_OUT_SPEED')

    def test_path_configuration(self):
        """Test that all path constants are defined."""
        path_attrs = [
            'BASE_DIR', 'DATA_DIR', 'DATA_RAW_DIR', 'DATA_PROCESSED_DIR',
            'NETCDF_DIR', 'PRICE_DIR', 'POWER_CURVE_DIR', 'SHAPEFILE_DIR',
            'WIND_POWER_DIR', 'REGIONS_DIR', 'CAPTURE_PRICE_DIR',
            'VALUE_FACTOR_DIR', 'FIGURES_DIR'
        ]

        for attr in path_attrs:
            assert hasattr(config, attr), f"Missing path constant: {attr}"
            path = getattr(config, attr)
            assert isinstance(path, Path), f"{attr} should be a Path object"

    def test_data_processing_parameters(self):
        """Test data processing parameter constants."""
        assert hasattr(config, 'PRICE_TIME_COL')
        assert hasattr(config, 'PRICE_VALUE_COL')
        assert hasattr(config, 'STANDARD_TIMEZONE')
        assert config.STANDARD_TIMEZONE == "UTC"


class TestConfigPaths:
    """Test configuration paths are properly structured."""

    def test_base_dir_is_project_root(self):
        """Test that BASE_DIR points to project root."""
        assert config.BASE_DIR.exists()
        assert (config.BASE_DIR / "config.py").exists()

    def test_data_dir_structure(self):
        """Test data directory structure."""
        assert config.DATA_DIR == config.BASE_DIR / "data"
        assert config.DATA_RAW_DIR == config.DATA_DIR / "raw"
        assert config.DATA_PROCESSED_DIR == config.DATA_DIR / "processed"

    def test_input_paths_under_raw(self):
        """Test input paths are under raw data directory."""
        assert config.NETCDF_DIR.parent == config.DATA_RAW_DIR
        assert config.PRICE_DIR.parent == config.DATA_RAW_DIR
        assert config.POWER_CURVE_DIR.parent == config.DATA_RAW_DIR

    def test_output_paths_under_processed(self):
        """Test output paths are under processed data directory."""
        assert config.WIND_POWER_DIR.parent == config.DATA_PROCESSED_DIR
        assert config.REGIONS_DIR.parent == config.DATA_PROCESSED_DIR
        assert config.CAPTURE_PRICE_DIR.parent == config.DATA_PROCESSED_DIR
        assert config.VALUE_FACTOR_DIR.parent == config.DATA_PROCESSED_DIR
