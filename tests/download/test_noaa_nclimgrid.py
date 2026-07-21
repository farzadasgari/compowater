"""
Tests for compowater.download.noaa_nclimgrid.
"""

from __future__ import annotations

from compowater.download.noaa_nclimgrid import build_tasks


def test_build_tasks_returns_one_task_per_month_in_range():
    tasks = build_tasks(2020, 2021)
    assert len(tasks) == 24  # 2 years x 12 months


def test_build_tasks_url_and_destination_follow_expected_pattern():
    tasks = build_tasks(2020, 2020)
    january = tasks[0]

    assert january.url.endswith("/grids/2020/ncdd-202001-grd-scaled.nc")
    assert january.destination.name == "ncdd-202001-grd-scaled.nc"
    assert "//" not in january.url.replace("https://", "")


def test_build_tasks_single_year_covers_all_twelve_months():
    tasks = build_tasks(2024, 2024)
    months = sorted(t.name.split("-")[-1] for t in tasks)
    assert months == [f"{m:02d}" for m in range(1, 13)]
