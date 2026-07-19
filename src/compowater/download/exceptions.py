"""Custom exceptions for the download pipeline."""

from __future__ import annotations


class DownloadError(Exception):
    """Base class for download-pipeline errors."""


class ResourceNotFoundError(DownloadError):
    """
    Raised when a remote URL returns HTTP 404.

    Common and often *expected* for near-real-time sources — e.g. NOAA
    publishes a given month's nClimGrid file some weeks after month-end,
    so recent months will 404 until then. Callers can catch this
    specifically and choose to skip rather than treat it as a failure.
    """
