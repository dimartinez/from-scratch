import os
import pytest
from pathlib import Path
from unittest.mock import patch


def copy_file(content, dest, backup=False):
    from src.sync.copy import copy_file
    return copy_file(content, dest, backup=backup)


def test_uses_tmp_file_then_rename(tmp_path, monkeypatch):
    dest = tmp_path / "file.md"
    tmp_created = []
    original_write_text = Path.write_text

    def tracking_write(self, *args, **kwargs):
        if ".tmp." in str(self):
            tmp_created.append(str(self))
        return original_write_text(self, *args, **kwargs)

    monkeypatch.setattr(Path, "write_text", tracking_write)
    copy_file("content", dest)
    assert len(tmp_created) == 1
    assert ".tmp." in tmp_created[0]


def test_destination_intact_if_rename_fails(tmp_path):
    dest = tmp_path / "file.md"
    dest.write_text("original content")

    with patch("src.sync.copy.os.rename", side_effect=OSError("rename failed")):
        try:
            copy_file("new content", dest)
        except OSError:
            pass
    assert dest.read_text() == "original content"


def test_no_dest_file_if_rename_fails_on_fresh_write(tmp_path):
    dest = tmp_path / "new_file.md"

    with patch("src.sync.copy.os.rename", side_effect=OSError("rename failed")):
        try:
            copy_file("content", dest)
        except OSError:
            pass
    assert not dest.exists()


def test_backup_created_before_write(tmp_path):
    dest = tmp_path / "file.md"
    dest.write_text("original")

    # Structural verification: backup has original content, dest has new content
    copy_file("new content", dest, backup=True)
    backups = list(tmp_path.glob("*.bak.*"))
    assert len(backups) == 1
    assert backups[0].read_text() == "original"
    assert dest.read_text() == "new content"


def test_no_tmp_files_left_after_successful_copy(tmp_path):
    dest = tmp_path / "file.md"
    copy_file("content", dest)
    tmp_files = list(tmp_path.glob("*.tmp.*"))
    assert tmp_files == []
