import json
import pytest
from pathlib import Path


def make_catalog(catalog_dir: Path, entries=None):
    """Create a minimal fake catalog directory."""
    catalog_dir.mkdir(parents=True, exist_ok=True)
    if entries is None:
        entries = [{"kind": "command", "source": "commands/foo.md"}]
    (catalog_dir / "catalog.json").write_text(json.dumps({"entries": entries}))
    (catalog_dir / "commands").mkdir(exist_ok=True)
    (catalog_dir / "commands" / "foo.md").write_text("# Foo command")
    return catalog_dir


def run_init(catalog_dir, dest_dir, state_file, force=False, stdin_text="s\n"):
    from src.commands.init import run_init
    import io
    out = io.StringIO()
    stdin = io.StringIO(stdin_text)
    return run_init(
        catalog_dir=catalog_dir,
        dest_dir=dest_dir,
        state_path=state_file,
        force=force,
        out=out,
        stdin=stdin,
    )


def test_init_installs_all_files(tmp_path):
    catalog_dir = make_catalog(tmp_path / "catalog")
    dest_dir = tmp_path / "claude"
    state_file = tmp_path / ".state.json"

    exit_code = run_init(catalog_dir, dest_dir, state_file)

    assert exit_code == 0
    assert (dest_dir / "commands" / "foo.md").exists()


def test_init_writes_state_file(tmp_path):
    catalog_dir = make_catalog(tmp_path / "catalog")
    dest_dir = tmp_path / "claude"
    state_file = tmp_path / ".state.json"

    run_init(catalog_dir, dest_dir, state_file)

    assert state_file.exists()
    state = json.loads(state_file.read_text())
    assert "installed_files" in state
    assert len(state["installed_files"]) == 1


def test_init_with_force_overwrites_with_backup(tmp_path):
    catalog_dir = make_catalog(tmp_path / "catalog")
    dest_dir = tmp_path / "claude"
    state_file = tmp_path / ".state.json"

    # First install
    run_init(catalog_dir, dest_dir, state_file)

    # Modify catalog content
    (catalog_dir / "commands" / "foo.md").write_text("# Updated foo")

    exit_code = run_init(catalog_dir, dest_dir, state_file, force=True)
    assert exit_code == 0
    backups = list((dest_dir / "commands").glob("*.bak.*"))
    assert len(backups) == 1


def test_init_with_preexisting_untracked_file_plants(tmp_path):
    catalog_dir = make_catalog(tmp_path / "catalog")
    dest_dir = tmp_path / "claude"
    state_file = tmp_path / ".state.json"

    # User has their own file
    (dest_dir / "commands").mkdir(parents=True)
    (dest_dir / "commands" / "foo.md").write_text("user's own content")

    exit_code = run_init(catalog_dir, dest_dir, state_file)
    # Should abort or return non-zero due to conflict
    assert exit_code != 0


def test_init_cancel_does_not_touch_disk(tmp_path):
    catalog_dir = make_catalog(tmp_path / "catalog")
    dest_dir = tmp_path / "claude"
    state_file = tmp_path / ".state.json"

    exit_code = run_init(catalog_dir, dest_dir, state_file, stdin_text="n\n")
    assert exit_code == 2
    assert not (dest_dir / "commands" / "foo.md").exists()
    assert not state_file.exists()
