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
