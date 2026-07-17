"""
Parallel download utilities.
"""

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed

from tqdm import tqdm


def download_many(
    tasks,
    worker,
    max_workers=8,
):
    """
    Execute download tasks concurrently.

    Parameters
    ----------
    tasks
        Iterable of task definitions.

    worker
        Function receiving one task.

    max_workers
        Number of concurrent workers.
    """

    results = []

    with ThreadPoolExecutor(
        max_workers=max_workers
    ) as executor:

        futures = {
            executor.submit(worker, task): task
            for task in tasks
        }

        for future in tqdm(
            as_completed(futures),
            total=len(futures),
            desc="Downloading",
        ):

            results.append(
                future.result()
            )

    return results