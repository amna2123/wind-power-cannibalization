"""Data processing and computation scripts.

This module contains scripts for:
- Converting ERA5 wind speed to power generation
- Extracting regional data from gridded datasets
- Calculating capture price and value factor metrics
- Computing zonal aggregations
"""

import sys
from pathlib import Path

# Add project root to Python path to enable imports
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
