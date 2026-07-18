"""
NOAA nClimGrid-Daily fetcher.

Builds one DatasetTask per (year, month) in the requested range.
Files are CONUS-wide gridded NetCDF (~one file per calendar month);
see registry.download_all() for how these merge with the YAML-declared
datasets into a single pipeline run.
"""

from __future__ import annotations

from compowater.paths import RAW_DATA_CLIMATE_DIR
from compowater.download.tasks import DatasetTask

BASE_URL = "https://www.ncei.noaa.gov/data/nclimgrid-daily/access/grids"
SOURCE_PAGE = "https://www.ncei.noaa.gov/products/land-based-station/nclimgrid-daily"


def build_tasks(start_year: int, end_year: int) -> list[DatasetTask]:
    """
    Build one DatasetTask per calendar month in [start_year, end_year] (inclusive).
    """
    tasks = []
    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            fname = f"ncdd-{year}{month:02d}-grd-scaled.nc"
            tasks.append(
                DatasetTask(
                    name=f"NOAA nClimGrid-Daily {year}-{month:02d}",
                    source_page=SOURCE_PAGE,
                    url=f"{BASE_URL}/{year}/{fname}",
                    destination=RAW_DATA_CLIMATE_DIR / fname,
                )
            )
    return tasks