"""
Tests for compowater.download.registry.

monkeypatching the place a function is used,
not the place it's defined. 
"""

from __future__ import annotations
import json
from pathlib import Path

import yaml

import compowater.download.registry as registry_module
from compowater.download.tasks import DatasetTask


def test_load_tasks_parses_yaml_into_dataset_tasks(tmp_path):
    config = {
        "datasets": [{
            "name": "Fake Dataset",
            "source_page": "https://example.gov/page",
            "url": "https://example.gov/data.csv",
            "destination": "data/raw/fake/data.csv",
        }]
    }
    config_path = tmp_path / "datasets.yaml"
    config_path.write_text(yaml.dump(config))

    tasks = registry_module.load_tasks(config_path=config_path)

    assert len(tasks) == 1
    assert tasks[0].name == "Fake Dataset"
    assert tasks[0].sha256 is None


def test_fetch_and_record_calls_download_file_and_writes_manifest(tmp_path, monkeypatch):
    fake_manifest = tmp_path / "_manifest.jsonl"
    monkeypatch.setattr(registry_module, "MANIFEST_PATH", fake_manifest)

    def fake_download_file(**kwargs):
        return kwargs["destination"], "fakehash123"

    monkeypatch.setattr(registry_module, "download_file", fake_download_file)

    task = DatasetTask(
        name="Fake Dataset", source_page="https://example.gov",
        url="https://example.gov/data.csv",
        destination=registry_module.PROJECT_ROOT / "data" / "raw" / "fake.csv",
    )

    result = registry_module._fetch_and_record(task)

    assert result[1] == "fakehash123"
    manifest_lines = fake_manifest.read_text().strip().splitlines()
    assert len(manifest_lines) == 1
    entry = json.loads(manifest_lines[0])
    assert entry["name"] == "Fake Dataset"
    assert entry["sha256"] == "fakehash123"


def test_fetch_and_record_skips_and_returns_none_on_404(tmp_path, monkeypatch):
    fake_manifest = tmp_path / "_manifest.jsonl"
    monkeypatch.setattr(registry_module, "MANIFEST_PATH", fake_manifest)

    def raise_not_found(**kwargs):
        raise registry_module.ResourceNotFoundError("not published yet")

    monkeypatch.setattr(registry_module, "download_file", raise_not_found)

    task = DatasetTask(
        name="Not Yet Published", source_page="https://example.gov",
        url="https://example.gov/future.csv",
        destination=registry_module.PROJECT_ROOT / "data" / "raw" / "future.csv",
    )

    result = registry_module._fetch_and_record(task)

    assert result is None
    assert not fake_manifest.exists()  # nothing written for a skipped task


def test_download_all_merges_yaml_and_noaa_tasks(monkeypatch):
    fake_yaml_tasks = [DatasetTask(
        name="CA Task", source_page="p", url="u", destination=Path("d"))]
    fake_noaa_tasks = [DatasetTask(
        name="NOAA Task", source_page="p", url="u", destination=Path("d"))]

    monkeypatch.setattr(registry_module, "load_tasks", lambda: fake_yaml_tasks)
    monkeypatch.setattr(registry_module, "build_tasks",
                        lambda start, end: fake_noaa_tasks)
    monkeypatch.setattr(registry_module, "download_many",
                        lambda tasks, worker, max_workers: tasks)

    assert len(registry_module.download_all(
        include_noaa=True)) == 2   # CA + NOAA
    assert len(registry_module.download_all(
        include_noaa=False)) == 1  # CA only


def test_download_all_does_not_mutate_the_list_returned_by_load_tasks(monkeypatch):
    shared_yaml_tasks = [DatasetTask(
        name="CA Task", source_page="p", url="u", destination=Path("d"))]
    noaa_tasks = [DatasetTask(
        name="NOAA Task", source_page="p", url="u", destination=Path("d"))]

    monkeypatch.setattr(registry_module, "load_tasks",
                        lambda: shared_yaml_tasks)
    monkeypatch.setattr(registry_module, "build_tasks",
                        lambda start, end: noaa_tasks)
    monkeypatch.setattr(registry_module, "download_many",
                        lambda tasks, worker, max_workers: tasks)

    registry_module.download_all(include_noaa=True)

    # Regression guard: a future load_tasks() (e.g. a cached/memoized
    # version) could return the same list object on every call.
    # download_all must never mutate what it was handed.
    assert len(shared_yaml_tasks) == 1
