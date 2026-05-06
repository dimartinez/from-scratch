import hashlib
import pytest
from pathlib import Path


def sha256(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def diff(catalog_entries, installed_files, dest_base):
    from src.sync.diff import compute_diff
    return compute_diff(catalog_entries, installed_files, dest_base)


def test_added_file(tmp_path):
    catalog = [{"path": "commands/foo.md", "content": "hello"}]
    installed = []
    result = diff(catalog, installed, tmp_path)
    assert len(result["added"]) == 1
    assert result["added"][0]["path"] == "commands/foo.md"


def test_unchanged_file(tmp_path):
    content = "hello"
    (tmp_path / "commands").mkdir()
    (tmp_path / "commands" / "foo.md").write_text(content)
    catalog = [{"path": "commands/foo.md", "content": content}]
    installed = [{"path": "commands/foo.md", "hash": sha256(content)}]
    result = diff(catalog, installed, tmp_path)
    assert len(result["unchanged"]) == 1
    assert result["added"] == []
    assert result["modified"] == []


def test_modified_file(tmp_path):
    old_content = "old"
    new_content = "new"
    (tmp_path / "commands").mkdir()
    (tmp_path / "commands" / "foo.md").write_text(old_content)
    catalog = [{"path": "commands/foo.md", "content": new_content}]
    installed = [{"path": "commands/foo.md", "hash": sha256(old_content)}]
    result = diff(catalog, installed, tmp_path)
    assert len(result["modified"]) == 1
    assert result["modified"][0]["path"] == "commands/foo.md"


def test_removed_file(tmp_path):
    content = "hello"
    installed = [{"path": "commands/foo.md", "hash": sha256(content)}]
    catalog = []  # No longer in catalog
    result = diff(catalog, installed, tmp_path)
    assert len(result["removed"]) == 1
    assert result["removed"][0]["path"] == "commands/foo.md"


def test_multiple_mixed(tmp_path):
    # Setup: one unchanged, one modified, one removed, one added
    (tmp_path / "commands").mkdir()
    (tmp_path / "commands" / "unchanged.md").write_text("same")
    (tmp_path / "commands" / "modified.md").write_text("old content")

    catalog = [
        {"path": "commands/unchanged.md", "content": "same"},
        {"path": "commands/modified.md", "content": "new content"},
        {"path": "commands/added.md", "content": "brand new"},
    ]
    installed = [
        {"path": "commands/unchanged.md", "hash": sha256("same")},
        {"path": "commands/modified.md", "hash": sha256("old content")},
        {"path": "commands/removed.md", "hash": sha256("gone")},
    ]
    result = diff(catalog, installed, tmp_path)
    assert len(result["added"]) == 1
    assert len(result["modified"]) == 1
    assert len(result["unchanged"]) == 1
    assert len(result["removed"]) == 1
