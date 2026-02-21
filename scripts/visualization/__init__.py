"""Figure generation and visualization scripts.

This module contains scripts for generating publication-quality figures:
- Model validation plots
- Temporal analysis charts
- Spatial pattern maps
- Trend visualizations
- Correlation analyses
- Geographic visualization
"""

import sys
from pathlib import Path

# Add project root to Python path to enable imports
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
