"""
Tests for compowater.download.parallel.

Testing concurrent code — check *what* the results are
(order-independent, since threads finish in unpredictable order) and
that a failing worker still surfaces its exception to the caller.
"""

from __future__ import annotations

from compowater.download.parallel import download_many


def test_download_many_runs_every_task_and_collects_results():
    tasks = [1, 2, 3, 4, 5]

    def worker(n: int) -> int:
        return n * 2

    results = download_many(tasks, worker, max_workers=3)
    # sorted: completion order isn't guaranteed
    assert sorted(results) == [2, 4, 6, 8, 10]


def test_download_many_propagates_a_worker_exception():
    tasks = [1, 2, 3]

    def worker(n: int) -> int:
        if n == 2:
            raise RuntimeError("boom")
        return n

    try:
        download_many(tasks, worker)
        assert False, "expected RuntimeError to propagate"
    except RuntimeError as exc:
        assert str(exc) == "boom"
