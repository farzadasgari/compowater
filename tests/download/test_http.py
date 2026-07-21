"""
Tests for compowater.download.http.

Mocking HTTP via requests-mock (no real network during
tests), and testing failure paths, not just the valid path.
"""

from __future__ import annotations

import hashlib

import pytest
import requests

from compowater.download.exceptions import ResourceNotFoundError
from compowater.download.http import create_session, download_file

CONTENT = b"latitude,longitude,value\n1,2,3\n"
URL = "https://example.gov/data.csv"


def test_download_writes_content_and_hash_matches(tmp_path, requests_mock):
    requests_mock.get(URL, content=CONTENT)
    dest = tmp_path / "data.csv"

    path, digest = download_file(
        dataset_name="Test",
        source_page="https://example.gov",
        url=URL,
        destination=dest,
    )

    assert path.read_bytes() == CONTENT
    assert digest == hashlib.sha256(CONTENT).hexdigest()
    assert not (tmp_path / "data.csv.part").exists()


def test_existing_file_is_skipped_by_default(tmp_path, requests_mock):
    dest = tmp_path / "data.csv"
    dest.write_bytes(CONTENT)
    requests_mock.get(URL, content=b"stale bytes")

    download_file(
        dataset_name="Test",
        source_page="https://example.gov",
        url=URL,
        destination=dest,
    )

    assert dest.read_bytes() == CONTENT
    assert requests_mock.call_count == 0


def test_overwrite_true_redownloads_existing_file(tmp_path, requests_mock):
    dest = tmp_path / "data.csv"
    dest.write_bytes(b"old bytes")
    requests_mock.get(URL, content=CONTENT)

    download_file(
        dataset_name="Test",
        source_page="https://example.gov",
        url=URL,
        destination=dest,
        overwrite=True,
    )

    assert dest.read_bytes() == CONTENT
    assert requests_mock.call_count == 1


def test_checksum_mismatch_raises_and_leaves_no_file_behind(tmp_path, requests_mock):
    requests_mock.get(URL, content=CONTENT)
    dest = tmp_path / "data.csv"

    with pytest.raises(ValueError, match="Checksum mismatch"):
        download_file(
            dataset_name="Test",
            source_page="https://example.gov",
            url=URL,
            destination=dest,
            expected_sha256="0" * 64,
        )

    assert not dest.exists()
    assert not (tmp_path / "data.csv.part").exists()


def test_404_raises_resource_not_found_and_creates_no_file(tmp_path, requests_mock):
    requests_mock.get(URL, status_code=404)
    dest = tmp_path / "data.csv"

    with pytest.raises(ResourceNotFoundError):
        download_file(
            dataset_name="Test",
            source_page="https://example.gov",
            url=URL,
            destination=dest,
        )

    assert not dest.exists()


def test_other_http_error_status_still_raises_generic_error(tmp_path, requests_mock):
    requests_mock.get(URL, status_code=500)
    dest = tmp_path / "data.csv"

    with pytest.raises(requests.HTTPError):
        download_file(
            dataset_name="Test",
            source_page="https://example.gov",
            url=URL,
            destination=dest,
        )


def test_interrupted_download_cleans_up_partial_file(
    tmp_path, requests_mock, monkeypatch
):
    requests_mock.get(URL, content=CONTENT)
    dest = tmp_path / "data.csv"

    def broken_iter_content(self, chunk_size):
        yield CONTENT[:5]
        raise requests.exceptions.ConnectionError("simulated drop")

    monkeypatch.setattr(requests.Response, "iter_content", broken_iter_content)

    with pytest.raises(requests.exceptions.ConnectionError):
        download_file(
            dataset_name="Test",
            source_page="https://example.gov",
            url=URL,
            destination=dest,
        )

    assert not dest.exists()
    assert not (tmp_path / "data.csv.part").exists()


def test_provided_session_is_reused_instead_of_creating_a_new_one(
    tmp_path, requests_mock, monkeypatch
):
    requests_mock.get(URL, content=CONTENT)
    dest = tmp_path / "data.csv"
    calls = {"create_session": 0}

    def fake_create_session():
        calls["create_session"] += 1
        return create_session()

    monkeypatch.setattr("compowater.download.http.create_session", fake_create_session)

    my_session = create_session()
    download_file(
        dataset_name="Test",
        source_page="https://example.gov",
        url=URL,
        destination=dest,
        session=my_session,
    )

    assert calls["create_session"] == 0
