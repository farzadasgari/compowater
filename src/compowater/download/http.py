"""
HTTP download utilities.

This module provides reusable functions for downloading
individual files over HTTP.
"""

from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from tqdm import tqdm


TIMEOUT = 60
CHUNK_SIZE = 8192


def create_session() -> requests.Session:
    """
    Create a requests session with automatic retries.
    """

    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=(500, 502, 503, 504),
        allowed_methods=("GET",),
    )

    adapter = HTTPAdapter(max_retries=retry)

    session = requests.Session()

    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session


def download_file(
    *,
    dataset_name: str,
    source_page: str,
    url: str,
    destination: Path,
    overwrite: bool = False,
) -> Path:
    """
    Download a single remote file.
    """

    destination.parent.mkdir(parents=True, exist_ok=True)

    if destination.exists() and not overwrite:
        print(f"✓ {destination.name} already exists.")
        return destination

    print("=" * 80)
    print(dataset_name)
    print("=" * 80)
    print(f"Source : {source_page}")
    print()

    session = create_session()

    response = session.get(
        url,
        stream=True,
        timeout=TIMEOUT,
    )

    response.raise_for_status()

    total = int(
        response.headers.get(
            "content-length",
            0,
        )
    )

    with open(destination, "wb") as file:

        with tqdm(
            total=total,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            desc=destination.name,
        ) as progress:

            for chunk in response.iter_content(
                chunk_size=CHUNK_SIZE
            ):

                if chunk:

                    file.write(chunk)
                    progress.update(len(chunk))

    print(f"\nSaved to:\n{destination}\n")

    return destination
