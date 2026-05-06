import os
import pytest
from pathlib import Path


def cleanup_orphans(dest_base):
    from src.sync.copy import cleanup_orphan_tmp_files
    return cleanup_orphan_tmp_files(dest_base)


def test_orphan_tmp_files_are_removed(tmp_path):
    # Create fake orphan temp files from a dead process
    orphan = tmp_path / "commands" / "foo.md.tmp.99999"
    orphan.parent.mkdir(parents=True)
    orphan.write_text("orphan content")

    cleanup_orphans(tmp_path)
    assert not orphan.exists()


def test_non_tmp_files_not_touched(tmp_path):
    regular = tmp_path / "commands" / "foo.md"
    regular.parent.mkdir(parents=True)
    regular.write_text("regular file")

    cleanup_orphans(tmp_path)
    assert regular.exists()


def test_cleanup_handles_nested_dirs(tmp_path):
    (tmp_path / "a" / "b").mkdir(parents=True)
    orphan1 = tmp_path / "a" / "f.md.tmp.12345"
    orphan2 = tmp_path / "a" / "b" / "g.md.tmp.67890"
    orphan1.write_text("o1")
    orphan2.write_text("o2")

    cleanup_orphans(tmp_path)
    assert not orphan1.exists()
    assert not orphan2.exists()


def test_cleanup_returns_count_of_removed(tmp_path):
    for i in range(3):
        (tmp_path / f"f{i}.md.tmp.{i}").write_text("orphan")
    count = cleanup_orphans(tmp_path)
    assert count == 3


def test_no_orphans_returns_zero(tmp_path):
    count = cleanup_orphans(tmp_path)
    assert count == 0
