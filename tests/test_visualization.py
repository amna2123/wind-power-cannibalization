"""Tests for visualization scripts.

This module contains tests for the figure generation scripts.
"""

import sys
from pathlib import Path

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import config


class TestFigureGeneration:
    """Test figure generation functionality."""

    def test_figures_directory_configuration(self):
        """Test that figures directory is properly configured."""
        assert config.FIGURES_DIR == config.BASE_DIR / "figures"

    @pytest.mark.skipif(
        not config.DATA_PROCESSED_DIR.exists(),
        reason="Processed data not available"
    )
    def test_figure_scripts_exist(self):
        """Test that all figure scripts exist."""
        script_dir = config.BASE_DIR / "scripts" / "visualization"

        expected_scripts = [
            "figure2.py",
            "figure3.py",
            "figure4.py",
            "figure5.py",
            "figure6.py",
            "figure7.py",
        ]

        for script in expected_scripts:
            script_path = script_dir / script
            assert script_path.exists(), f"Missing figure script: {script}"


class TestVisualizationOutputs:
    """Test visualization output handling."""

    def test_output_directory_creation(self, temp_output_dir):
        """Test that output directories can be created."""
        assert temp_output_dir.exists()
        assert temp_output_dir.is_dir()

        # Test subdirectory creation
        subdir = temp_output_dir / "test_figures"
        subdir.mkdir(parents=True, exist_ok=True)
        assert subdir.exists()


@pytest.mark.integration
class TestFigureIntegration:
    """Integration tests for figure generation.

    These tests require actual data and are skipped if not available.
    """

    @pytest.mark.skipif(
        not config.DATA_PROCESSED_DIR.exists(),
        reason="Processed data not available"
    )
    def test_generate_all_figures(self):
        """Test generation of all figures."""
        pytest.skip("Integration test - requires full data and implementation")
