import time
import pytest
from pathlib import Path


def copy_file(src_content, dest, backup=False):
    from src.sync.copy import copy_file
    return copy_file(src_content, dest, backup=backup)


def test_simple_copy(tmp_path):
    dest = tmp_path / "commands" / "foo.md"
    copy_file("hello world", dest)
    assert dest.read_text() == "hello world"


def test_creates_intermediate_dirs(tmp_path):
    dest = tmp_path / "a" / "b" / "c" / "file.md"
    copy_file("content", dest)
    assert dest.exists()
    assert dest.read_text() == "content"


def test_backup_created_before_overwrite(tmp_path):
    dest = tmp_path / "file.md"
    dest.write_text("original")
    copy_file("new content", dest, backup=True)
    # Find backup file
    backups = list(tmp_path.glob("file.md.bak.*"))
    assert len(backups) == 1
    assert backups[0].read_text() == "original"


def test_backup_has_timestamp(tmp_path):
    dest = tmp_path / "file.md"
    dest.write_text("original")
    copy_file("new content", dest, backup=True)
    backups = list(tmp_path.glob("file.md.bak.*"))
    assert len(backups) == 1
    # Backup name contains a timestamp (digits)
    suffix = backups[0].name.split(".bak.")[-1]
    assert suffix.isdigit()


def test_destination_content_correct_after_copy(tmp_path):
    dest = tmp_path / "file.md"
    dest.write_text("old content")
    copy_file("brand new content", dest, backup=True)
    assert dest.read_text() == "brand new content"


def test_copy_no_backup_when_not_requested(tmp_path):
    dest = tmp_path / "file.md"
    dest.write_text("original")
    copy_file("new", dest, backup=False)
    backups = list(tmp_path.glob("*.bak.*"))
    assert len(backups) == 0
