"""
Project path definitions.

Defines project directories only — this module performs no filesystem
I/O on import.
"""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SRC_DIR = PROJECT_ROOT / "src"
DATA_DIR = PROJECT_ROOT / "data"

RAW_DATA_DIR = DATA_DIR / "raw"
INTERMEDIATE_DATA_DIR = DATA_DIR / "intermediate"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

RAW_DATA_CLIMATE_DIR = RAW_DATA_DIR / "climate"
RAW_DATA_RESERVOIRS_DIR = RAW_DATA_DIR / "reservoirs"
RAW_DATA_URBAN_WATER_DIR = RAW_DATA_DIR / "urban_water"

ALL_DATA_DIRS = (
    DATA_DIR,
    RAW_DATA_DIR,
    INTERMEDIATE_DATA_DIR,
    PROCESSED_DATA_DIR,
    RAW_DATA_CLIMATE_DIR,
    RAW_DATA_RESERVOIRS_DIR,
    RAW_DATA_URBAN_WATER_DIR,
)

CONFIG = PROJECT_ROOT / "config"

DATASETS_CONFIG = CONFIG / "datasets.yaml"
MANIFEST_PATH = RAW_DATA_DIR / "_manifest.jsonl"


def ensure_data_dirs() -> None:
    """Create all project data directories if they don't already exist."""
    for directory in ALL_DATA_DIRS:
        directory.mkdir(parents=True, exist_ok=True)
