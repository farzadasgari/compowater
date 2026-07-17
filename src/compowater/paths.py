"""
Project path definitions.

This module centralizes all project directories used throughout
the Compowater workflow.
"""

from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Main directories
SRC_DIR = PROJECT_ROOT / "src"
DATA_DIR = PROJECT_ROOT / "data"

# Data directories
RAW_DATA_DIR = DATA_DIR / "raw"
INTERMEDIATE_DATA_DIR = DATA_DIR / "intermediate"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Raw datasets
RAW_DATA_RESERVOIRS_DIR = RAW_DATA_DIR / "reservoirs"
RAW_DATA_URBAN_WATER_DIR = RAW_DATA_DIR / "urban_water"

# Create directories if they do not exist
for directory in (
    DATA_DIR,
    RAW_DATA_DIR,
    INTERMEDIATE_DATA_DIR,
    PROCESSED_DATA_DIR,
    RAW_DATA_RESERVOIRS_DIR,
    RAW_DATA_URBAN_WATER_DIR,
):
    directory.mkdir(parents=True, exist_ok=True)
