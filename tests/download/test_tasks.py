"""
Tests for compowater.download.tasks.

Confirming a dataclass behaves the way its definition promises.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from compowater.download.tasks import DatasetTask


def test_dataset_task_holds_the_values_it_was_given():
    task = DatasetTask(
        name="Test Dataset",
        source_page="https://example.gov",
        url="https://example.gov/data.csv",
        destination=Path("data/raw/example/data.csv"),
    )

    assert task.name == "Test Dataset"
    assert task.sha256 is None  # default, since we didn't provide one


def test_dataset_task_is_immutable():
    task = DatasetTask(
        name="Test Dataset",
        source_page="https://example.gov",
        url="https://example.gov/data.csv",
        destination=Path("data/raw/example/data.csv"),
    )

    with pytest.raises(AttributeError):
        task.name = "Changed"
