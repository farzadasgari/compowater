# src/compowater/download/tasks.py

"""
Shared task definition for the download pipeline.

Kept in its own module — deliberately with no imports from registry.py
or any source-specific fetcher — so multiple modules can depend on
DatasetTask without creating a circular import between them.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DatasetTask:
    name: str
    source_page: str
    url: str
    destination: Path
    sha256: str | None = None
