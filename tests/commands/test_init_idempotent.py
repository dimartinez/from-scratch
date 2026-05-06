import io
import json
import pytest
from pathlib import Path
from datetime import datetime, timezone


def make_catalog(catalog_dir: Path):
    catalog_dir.mkdir(parents=True, exist_ok=True)
    (catalog_dir / "catalog.json").write_text(json.dumps({"entries": [{"kind": "command", "source": "commands/foo.md"}]}))
    (catalog_dir / "commands").mkdir(exist_ok=True)
    (catalog_dir / "commands" / "foo.md").write_text("# Foo")
    return catalog_dir


def run_init(catalog_dir, dest_dir, state_file, force=False, stdin_text="s\n"):
    from src.commands.init import run_init
    out = io.StringIO()
    stdin = io.StringIO(stdin_text)
    return run_init(catalog_dir=catalog_dir, dest_dir=dest_dir, state_path=state_file, force=force, out=out, stdin=stdin), out.getvalue()


def make_complete_state(state_file, dest_dir):
    from src.state.state import compute_hash, write_state
    content = "# Foo"
    state = {
        "last_sync_started_at": "2026-01-01T00:00:00Z",
        "last_sync_completed_at": "2026-01-01T00:01:00Z",
        "installed_files": [{"path": "commands/foo.md", "hash": compute_hash(content)}],
        "catalog_version": "",
        "has_incomplete_sync": False,
    }
    write_state(state, state_file)
    (dest_dir / "commands").mkdir(parents=True, exist_ok=True)
    (dest_dir / "commands" / "foo.md").write_text(content)


def test_init_already_complete_exits_0_no_disk_change(tmp_path):
    catalog_dir = make_catalog(tmp_path / "catalog")
    dest_dir = tmp_path / "claude"
    state_file = tmp_path / ".state.json"
    make_complete_state(state_file, dest_dir)

    mtime_before = (dest_dir / "commands" / "foo.md").stat().st_mtime
    exit_code, output = run_init(catalog_dir, dest_dir, state_file)
    mtime_after = (dest_dir / "commands" / "foo.md").stat().st_mtime

    assert exit_code == 0
    assert mtime_before == mtime_after


def test_init_already_complete_prints_hint(tmp_path):
    catalog_dir = make_catalog(tmp_path / "catalog")
    dest_dir = tmp_path / "claude"
    state_file = tmp_path / ".state.json"
    make_complete_state(state_file, dest_dir)

    _, output = run_init(catalog_dir, dest_dir, state_file)
    assert "from-scratch update" in output or "inicializado" in output


def test_init_force_over_complete_advances(tmp_path):
    catalog_dir = make_catalog(tmp_path / "catalog")
    dest_dir = tmp_path / "claude"
    state_file = tmp_path / ".state.json"
    make_complete_state(state_file, dest_dir)

    # Update catalog content
    (catalog_dir / "commands" / "foo.md").write_text("# Updated")

    exit_code, _ = run_init(catalog_dir, dest_dir, state_file, force=True)
    assert exit_code == 0
    assert (dest_dir / "commands" / "foo.md").read_text() == "# Updated"
