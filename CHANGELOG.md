# Changelog

## [0.1.0] - 2026-07-21
### Added
- Data acquisition pipeline: CA DWR reservoir data, CA urban water
  supply/demand data, NOAA nClimGrid-Daily climate grids.
- Retry logic, SHA-256 checksum verification, and atomic (crash-safe)
  writes in the HTTP download layer.
- YAML-driven dataset registry with a provenance manifest.
- Graceful skip-and-continue handling for not-yet-published NOAA
  months (HTTP 404).
- Dual pip/conda environment support.
- CLI entry point: `scripts/run_download_pipeline.py`.
- `CITATION.cff` for machine-readable citation.