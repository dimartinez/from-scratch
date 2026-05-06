import hashlib
import pytest
from pathlib import Path


def sha256(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def diff(catalog, installed, dest_base):
    from src.sync.diff import compute_diff
    return compute_diff(catalog, installed, dest_base)


def test_disk_differs_from_recorded_categorized_as_user_modified(tmp_path):
    original = "original content"
    user_modified = "user modified content"
    catalog_new = "catalog update"

    (tmp_path / "commands").mkdir()
    (tmp_path / "commands" / "foo.md").write_text(user_modified)

    catalog = [{"path": "commands/foo.md", "content": catalog_new}]
    installed = [{"path": "commands/foo.md", "hash": sha256(original)}]

    result = diff(catalog, installed, tmp_path)
    assert len(result["user_modified"]) == 1
    assert result["user_modified"][0]["path"] == "commands/foo.md"
    assert result["user_modified"][0]["has_remote_update"] is True


def test_user_modified_with_no_remote_update(tmp_path):
    original = "original content"
    user_modified = "user modified"

    (tmp_path / "commands").mkdir()
    (tmp_path / "commands" / "foo.md").write_text(user_modified)

    # Catalog has the same content as what we originally installed
    catalog = [{"path": "commands/foo.md", "content": original}]
    installed = [{"path": "commands/foo.md", "hash": sha256(original)}]

    result = diff(catalog, installed, tmp_path)
    assert len(result["user_modified"]) == 1
    assert result["user_modified"][0]["has_remote_update"] is False


def test_matching_hash_not_categorized_as_user_modified(tmp_path):
    content = "unchanged content"
    (tmp_path / "commands").mkdir()
    (tmp_path / "commands" / "foo.md").write_text(content)

    catalog = [{"path": "commands/foo.md", "content": content}]
    installed = [{"path": "commands/foo.md", "hash": sha256(content)}]

    result = diff(catalog, installed, tmp_path)
    assert result["user_modified"] == []
    assert len(result["unchanged"]) == 1


def test_user_modified_not_in_other_categories(tmp_path):
    original = "original"
    user_version = "user changed"
    catalog_update = "catalog update"

    (tmp_path / "commands").mkdir()
    (tmp_path / "commands" / "foo.md").write_text(user_version)

    catalog = [{"path": "commands/foo.md", "content": catalog_update}]
    installed = [{"path": "commands/foo.md", "hash": sha256(original)}]

    result = diff(catalog, installed, tmp_path)
    assert result["added"] == []
    assert result["modified"] == []
    assert result["unchanged"] == []
