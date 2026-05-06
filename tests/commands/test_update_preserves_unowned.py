import io
import json
import subprocess
from pathlib import Path


def make_catalog_and_clone(tmp_path, content="# Foo"):
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


def test_update_does_not_touch_untracked_user_files(tmp_path):
    from src.commands.update import run_update
    from src.state.state import compute_hash, write_state

    clone = make_catalog_and_clone(tmp_path, content="# Updated")
    dest_dir = tmp_path / "claude"
    state_file = tmp_path / ".state.json"

    # Install the tracked file
    (dest_dir / "commands").mkdir(parents=True)
    (dest_dir / "commands" / "foo.md").write_text("# Foo")

    # User's own file not in catalog
    (dest_dir / "commands" / "my-custom.md").write_text("my custom command")

    write_state({
        "last_sync_started_at": "2026-01-01T00:00:00Z",
        "last_sync_completed_at": "2026-01-01T00:01:00Z",
        "installed_files": [{"path": "commands/foo.md", "hash": compute_hash("# Foo")}],
        "catalog_version": "",
        "has_incomplete_sync": False,
    }, state_file)

    run_update(clone_dir=clone, dest_dir=dest_dir, state_path=state_file,
               out=io.StringIO(), stdin=io.StringIO("s\n"), skip_pull=True)

    # User file should still exist untouched
    assert (dest_dir / "commands" / "my-custom.md").exists()
    assert (dest_dir / "commands" / "my-custom.md").read_text() == "my custom command"
