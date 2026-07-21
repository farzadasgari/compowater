"""Parallel download utilities."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import TypeVar

from tqdm import tqdm

TaskT = TypeVar("TaskT")
ResultT = TypeVar("ResultT")


def download_many(
    tasks: Iterable[TaskT],
    worker: Callable[[TaskT], ResultT],
    max_workers: int = 8,
) -> list[ResultT]:
    """
    Execute tasks concurrently.

    Returns results in *completion* order, not submission order — if
    downstream code needs task[i] <-> result[i] correspondence, sort
    by a task identifier afterward rather than assuming index alignment.
    """
    results: list[ResultT] = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(worker, task): task for task in tasks}
        for future in tqdm(
            as_completed(futures), total=len(futures), desc="Downloading"
        ):
            results.append(future.result())
    return results
