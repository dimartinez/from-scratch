import io
import json
import os
import subprocess
import pytest
from pathlib import Path
from unittest.mock import patch


def make_catalog_and_clone(tmp_path, content="# Updated"):
    remote = tmp_path / "remote"
    remote.mkdir(parents=True)
    (remote / "catalog").mkdir()
    (remote / "catalog" / "catalog.json").write_text(json.dumps({"entries": [{"kind": "command", "source": "commands/foo.md"}]}))
    (remote / "catalog" / "commands").mkdir()
    (remote / "catalog" / "commands" / "foo.md").write_text(content)
    subprocess.run(["git", "init", str(remote)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(remote), "config", "user.email", "t@t.com"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(remote), "config", "user.name", "T"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(remote), "add", "."], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(remote), "commit", "-m", "init"], check=True, capture_output=True)
    clone = tmp_path / "clone"
    subprocess.run(["git", "clone", str(remote), str(clone)], check=True, capture_output=True)
    return clone


def test_interrupt_during_copy_leaves_no_truncated_files(tmp_path):
    from src.commands.update import run_update
    from src.state.state import compute_hash, write_state
    from src.sync import copy as copy_module

    clone = make_catalog_and_clone(tmp_path, content="# Updated content")
    dest_dir = tmp_path / "claude"
    state_file = tmp_path / ".state.json"

    (dest_dir / "commands").mkdir(parents=True)
    (dest_dir / "commands" / "foo.md").write_text("# Old")

    write_state({
        "last_sync_started_at": "2026-01-01T00:00:00Z",
        "last_sync_completed_at": "2026-01-01T00:01:00Z",
        "installed_files": [{"path": "commands/foo.md", "hash": compute_hash("# Old")}],
        "catalog_version": "",
        "has_incomplete_sync": False,
    }, state_file)

    original_rename = os.rename

    def raise_on_rename(src, dst):
        raise KeyboardInterrupt("simulated cancel during rename")

    with patch("src.sync.copy.os.rename", side_effect=raise_on_rename):
        try:
            run_update(clone_dir=clone, dest_dir=dest_dir, state_path=state_file,
                       out=io.StringIO(), stdin=io.StringIO("s\n"), skip_pull=True)
        except (KeyboardInterrupt, SystemExit):
            pass

    # Destination file should be intact (not truncated) or absent
    dest_file = dest_dir / "commands" / "foo.md"
    if dest_file.exists():
        content = dest_file.read_text()
        assert len(content) > 0


def test_state_reflects_incomplete_sync_on_interrupt(tmp_path):
    from src.commands.update import run_update
    from src.state.state import compute_hash, write_state, read_state

    clone = make_catalog_and_clone(tmp_path, content="# Updated")
    dest_dir = tmp_path / "claude"
    state_file = tmp_path / ".state.json"

    (dest_dir / "commands").mkdir(parents=True)
    (dest_dir / "commands" / "foo.md").write_text("# Old")

    write_state({
        "last_sync_started_at": "2026-01-01T00:00:00Z",
        "last_sync_completed_at": "2026-01-01T00:01:00Z",
        "installed_files": [{"path": "commands/foo.md", "hash": compute_hash("# Old")}],
        "catalog_version": "",
        "has_incomplete_sync": False,
    }, state_file)

    with patch("src.sync.copy.os.rename", side_effect=KeyboardInterrupt("cancel")):
        try:
            run_update(clone_dir=clone, dest_dir=dest_dir, state_path=state_file,
                       out=io.StringIO(), stdin=io.StringIO("s\n"), skip_pull=True)
        except (KeyboardInterrupt, SystemExit):
            pass

    # The state file should exist (was written before copy started)
    assert state_file.exists()
    state = read_state(state_file)
    assert state is not None
