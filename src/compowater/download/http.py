"""HTTP download utilities with retry, progress, and checksum provenance."""

from __future__ import annotations
import hashlib
import logging
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from tqdm import tqdm

from compowater.download.exceptions import ResourceNotFoundError

logger = logging.getLogger(__name__)
TIMEOUT = 60
CHUNK_SIZE = 8192


def create_session() -> requests.Session:
    """Create a requests session with automatic retries on transient errors."""
    retry = Retry(total=3, backoff_factor=1,
                  status_forcelist=(500, 502, 503, 504),
                  allowed_methods=("GET",))
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
    expected_sha256: str | None = None,
    overwrite: bool = False,
    session: requests.Session | None = None,
) -> tuple[Path, str]:
    destination.parent.mkdir(parents=True, exist_ok=True)

    if destination.exists() and not overwrite:
        logger.info("%s already exists, skipping download.", destination.name)
        return destination, _sha256_of(destination)

    logger.info("Downloading %s from %s", dataset_name, source_page)
    active_session = session or create_session()
    response = active_session.get(url, stream=True, timeout=TIMEOUT)
    if response.status_code == 404:
        raise ResourceNotFoundError(f"404 Not Found: {url}")
    response.raise_for_status()

    total = int(response.headers.get("content-length", 0))
    hasher = hashlib.sha256()

    # Write to a sibling temp file first. A crash or dropped connection
    # mid-stream then leaves no file at `destination` at all — instead
    # of a truncated one that overwrite=False would mistake for good data.
    tmp_destination = destination.with_name(destination.name + ".part")

    try:
        with open(tmp_destination, "wb") as file, tqdm(
            total=total, unit="B", unit_scale=True, unit_divisor=1024,
            desc=destination.name,
        ) as progress:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    file.write(chunk)
                    hasher.update(chunk)
                    progress.update(len(chunk))

        digest = hasher.hexdigest()

        if expected_sha256 is not None and digest != expected_sha256:
            raise ValueError(
                f"Checksum mismatch for {destination.name}: "
                f"expected {expected_sha256}, got {digest}."
            )

        tmp_destination.replace(destination)  # atomic on POSIX and Windows

    except Exception:
        tmp_destination.unlink(missing_ok=True)
        raise

    logger.info("Saved %s (sha256=%s)", destination, digest)
    return destination, digest


def _sha256_of(path: Path) -> str:
    """Compute a file's SHA-256 hash, streaming to avoid loading it fully into memory."""
    hasher = hashlib.sha256()
    with open(path, "rb") as file:
        for chunk in iter(lambda: file.read(CHUNK_SIZE), b""):
            hasher.update(chunk)
    return hasher.hexdigest()
