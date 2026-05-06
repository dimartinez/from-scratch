import json
import pytest


def test_read_nonexistent_state_returns_none(tmp_path):
    from src.state.state import read_state
    result = read_state(tmp_path / ".state.json")
    assert result is None


def test_write_and_read_preserves_structure(tmp_path):
    from src.state.state import read_state, write_state
    state = {
        "last_sync_started_at": "2026-01-01T00:00:00Z",
        "last_sync_completed_at": "2026-01-01T00:01:00Z",
        "installed_files": [],
        "catalog_version": "abc123",
    }
    path = tmp_path / ".state.json"
    write_state(state, path)
    result = read_state(path)
    assert result == state


def test_json_keys_are_snake_case(tmp_path):
    from src.state.state import write_state
    state = {
        "last_sync_started_at": "2026-01-01T00:00:00Z",
        "last_sync_completed_at": "2026-01-01T00:01:00Z",
        "installed_files": [],
        "catalog_version": "abc123",
    }
    path = tmp_path / ".state.json"
    write_state(state, path)
    raw = json.loads(path.read_text())
    assert "last_sync_started_at" in raw
    assert "last_sync_completed_at" in raw
    assert "installed_files" in raw


def test_has_incomplete_sync_when_started_not_completed(tmp_path):
    from src.state.state import has_incomplete_sync
    state = {
        "last_sync_started_at": "2026-01-01T00:00:00Z",
        "last_sync_completed_at": None,
        "installed_files": [],
        "catalog_version": "abc123",
    }
    assert has_incomplete_sync(state) is True


def test_no_incomplete_sync_when_completed_after_started(tmp_path):
    from src.state.state import has_incomplete_sync
    state = {
        "last_sync_started_at": "2026-01-01T00:00:00Z",
        "last_sync_completed_at": "2026-01-01T00:01:00Z",
        "installed_files": [],
        "catalog_version": "abc123",
    }
    assert has_incomplete_sync(state) is False


def test_no_incomplete_sync_when_never_started():
    from src.state.state import has_incomplete_sync
    state = {
        "last_sync_started_at": None,
        "last_sync_completed_at": None,
        "installed_files": [],
        "catalog_version": "",
    }
    assert has_incomplete_sync(state) is False


def test_write_creates_parent_dirs(tmp_path):
    from src.state.state import write_state
    state = {"installed_files": [], "catalog_version": ""}
    path = tmp_path / "nested" / "dirs" / ".state.json"
    write_state(state, path)
    assert path.exists()
