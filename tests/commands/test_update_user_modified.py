import io
import json
import subprocess
from pathlib import Path


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


def setup_with_drift(tmp_path, state_file, dest_dir, installed_content, disk_content, catalog_content="# Updated"):
    from src.state.state import compute_hash, write_state
    (dest_dir / "commands").mkdir(parents=True, exist_ok=True)
    (dest_dir / "commands" / "foo.md").write_text(disk_content)
    write_state({
        "last_sync_started_at": "2026-01-01T00:00:00Z",
        "last_sync_completed_at": "2026-01-01T00:01:00Z",
        "installed_files": [{"path": "commands/foo.md", "hash": compute_hash(installed_content)}],
        "catalog_version": "",
        "has_incomplete_sync": False,
    }, state_file)


def test_user_modified_not_overwritten_without_force(tmp_path):
    from src.commands.update import run_update
    clone = make_catalog_and_clone(tmp_path)
    dest_dir = tmp_path / "claude"
    state_file = tmp_path / ".state.json"

    setup_with_drift(tmp_path, state_file, dest_dir,
                     installed_content="# Original",
                     disk_content="# User's changes")

    out = io.StringIO()
    code = run_update(clone_dir=clone, dest_dir=dest_dir, state_path=state_file,
                      force=False, out=out, stdin=io.StringIO("s\n"), skip_pull=True)

    assert (dest_dir / "commands" / "foo.md").read_text() == "# User's changes"


def test_user_modified_shown_with_exclamation_prefix(tmp_path):
    from src.commands.update import run_update
    clone = make_catalog_and_clone(tmp_path)
    dest_dir = tmp_path / "claude"
    state_file = tmp_path / ".state.json"

    setup_with_drift(tmp_path, state_file, dest_dir,
                     installed_content="# Original",
                     disk_content="# User's changes")

    out = io.StringIO()
    run_update(clone_dir=clone, dest_dir=dest_dir, state_path=state_file,
               force=False, out=out, stdin=io.StringIO("s\n"), skip_pull=True)
    assert "!" in out.getvalue()


def test_user_modified_overwritten_with_force_backup(tmp_path):
    from src.commands.update import run_update
    clone = make_catalog_and_clone(tmp_path, content="# Updated")
    dest_dir = tmp_path / "claude"
    state_file = tmp_path / ".state.json"

    setup_with_drift(tmp_path, state_file, dest_dir,
                     installed_content="# Original",
                     disk_content="# User's changes")

    out = io.StringIO()
    code = run_update(clone_dir=clone, dest_dir=dest_dir, state_path=state_file,
                      force=True, out=out, stdin=io.StringIO("s\n"), skip_pull=True)

    assert code == 0
    backups = list((dest_dir / "commands").glob("*.bak.*"))
    assert len(backups) == 1
    assert backups[0].read_text() == "# User's changes"
