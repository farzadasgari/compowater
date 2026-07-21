"""
Tests for compowater.paths.

Testing filesystem side effects without touching the real
repo — redirect the module's own directory list via monkeypatch,
point it at tmp_path instead.
"""

from __future__ import annotations
import compowater.paths as paths_module


def test_project_root_contains_expected_top_level_folders():
    assert (paths_module.PROJECT_ROOT / "src").is_dir()
    assert (paths_module.PROJECT_ROOT / "config").is_dir()


def test_ensure_data_dirs_creates_all_declared_directories(tmp_path, monkeypatch):
    fake_dirs = tuple(tmp_path / f"dir_{i}" for i in range(len(paths_module.ALL_DATA_DIRS)))
    monkeypatch.setattr(paths_module, "ALL_DATA_DIRS", fake_dirs)

    for d in fake_dirs:
        assert not d.exists()

    paths_module.ensure_data_dirs()

    for d in fake_dirs:
        assert d.is_dir()


def test_ensure_data_dirs_is_idempotent(tmp_path, monkeypatch):
    fake_dir = tmp_path / "some_dir"
    monkeypatch.setattr(paths_module, "ALL_DATA_DIRS", (fake_dir,))

    paths_module.ensure_data_dirs()
    paths_module.ensure_data_dirs()  # must not raise the second time

    assert fake_dir.is_dir()