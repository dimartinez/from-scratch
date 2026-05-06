import hashlib
import pytest
from pathlib import Path


def sha256(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def diff(catalog, installed, dest_base):
    from src.sync.diff import compute_diff
    return compute_diff(catalog, installed, dest_base)


def test_file_exists_not_in_state_is_unowned_conflict(tmp_path):
    # User had their own file before init
    (tmp_path / "commands").mkdir()
    (tmp_path / "commands" / "new-project.md").write_text("user's own content")

    catalog = [{"path": "commands/new-project.md", "content": "catalog content"}]
    installed = []  # Not in state

    result = diff(catalog, installed, tmp_path)
    assert len(result["unowned_conflict"]) == 1
    assert result["unowned_conflict"][0]["path"] == "commands/new-project.md"


def test_unowned_conflict_not_in_added(tmp_path):
    (tmp_path / "commands").mkdir()
    (tmp_path / "commands" / "foo.md").write_text("user content")

    catalog = [{"path": "commands/foo.md", "content": "catalog content"}]
    installed = []

    result = diff(catalog, installed, tmp_path)
    assert result["added"] == []
    assert len(result["unowned_conflict"]) == 1


def test_no_conflict_when_file_absent_and_not_in_state(tmp_path):
    catalog = [{"path": "commands/foo.md", "content": "catalog content"}]
    installed = []

    result = diff(catalog, installed, tmp_path)
    assert result["unowned_conflict"] == []
    assert len(result["added"]) == 1
