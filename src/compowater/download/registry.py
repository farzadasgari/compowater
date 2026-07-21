"""Single source of truth for what gets downloaded, from where, to where."""

from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
import logging
import yaml

from compowater.paths import PROJECT_ROOT, DATASETS_CONFIG, MANIFEST_PATH
from compowater.download.http import download_file
from compowater.download.parallel import download_many
from compowater.download.noaa_nclimgrid import build_tasks
from compowater.download.tasks import DatasetTask
from compowater.download.exceptions import ResourceNotFoundError


logger = logging.getLogger(__name__)


def load_tasks(config_path: Path = DATASETS_CONFIG) -> list[DatasetTask]:
    with open(config_path, "r", encoding="utf-8") as file:
        raw = yaml.safe_load(file)
    return [
        DatasetTask(
            name=entry["name"],
            source_page=entry["source_page"],
            url=entry["url"],
            destination=PROJECT_ROOT / entry["destination"],
            sha256=entry.get("sha256"),
        )
        for entry in raw["datasets"]
    ]


def _fetch_and_record(task: DatasetTask) -> tuple[Path, str] | None:
    try:
        path, digest = download_file(
            dataset_name=task.name, source_page=task.source_page,
            url=task.url, destination=task.destination,
            expected_sha256=task.sha256,
        )
    except ResourceNotFoundError as exc:
        logger.warning("Skipping %s (not available yet): %s", task.name, exc)
        return None
    _append_manifest(task, digest)
    return path, digest


def _append_manifest(task: DatasetTask, digest: str) -> None:
    """Record provenance: what was downloaded, from where, and its hash at that moment."""
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "name": task.name,
        "url": task.url,
        "destination": str(task.destination.relative_to(PROJECT_ROOT)),
        "sha256": digest,
        "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    with open(MANIFEST_PATH, "a", encoding="utf-8") as file:
        file.write(json.dumps(entry) + "\n")


def download_all(
    max_workers: int = 4,
    include_noaa: bool = True,
    noaa_start_year: int = 1991,
    noaa_end_year: int = 2026,
):
    tasks = list(load_tasks())

    if include_noaa:
        tasks += build_tasks(noaa_start_year, noaa_end_year)

    results = download_many(tasks, _fetch_and_record, max_workers=max_workers)
    succeeded = [r for r in results if r is not None]

    logger.warning(
        "download_all complete: %d succeeded, %d skipped (not yet available)",
        len(succeeded), len(results) - len(succeeded),
    )
    return succeeded


if __name__ == "__main__":
    download_all()
