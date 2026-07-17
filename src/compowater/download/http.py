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