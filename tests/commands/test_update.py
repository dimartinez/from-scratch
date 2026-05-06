import io
import json
import subprocess
import pytest
from pathlib import Path


def make_git_repo(path: Path, catalog_content="# Foo command") -> None:
    path.mkdir(parents=True, exist_ok=True)
    (path / "catalog").mkdir()
    (path / "catalog" / "catalog.json").write_text(json.dumps({
        "entries": [{"kind": "command", "source": "commands/foo.md"}]
    }))
    (path / "catalog" / "commands").mkdir()
    (path / "catalog" / "commands" / "foo.md").write_text(catalog_content)
    subprocess.run(["git", "init", str(path)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(path), "config", "user.email", "t@t.com"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(path), "config", "user.name", "T"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(path), "add", "."], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(path), "commit", "-m", "init"], check=True, capture_output=True)


def run_update(clone_dir, dest_dir, state_file, force=False, stdin_text="s\n"):
    from src.commands.update import run_update
    out = io.StringIO()
    stdin = io.StringIO(stdin_text)
    code = run_update(
        clone_dir=clone_dir,
        dest_dir=dest_dir,
        state_path=state_file,
        force=force,
        out=out,
        stdin=stdin,
        skip_pull=True,  # For testing, skip actual git pull
    )
    return code, out.getvalue()


def setup_installed(dest_dir, state_file, content="# Foo command"):
    from src.state.state import compute_hash, write_state
    (dest_dir / "commands").mkdir(parents=True, exist_ok=True)
    (dest_dir / "commands" / "foo.md").write_text(content)
    write_state({
        "last_sync_started_at": "2026-01-01T00:00:00Z",
        "last_sync_completed_at": "2026-01-01T00:01:00Z",
        "installed_files": [{"path": "commands/foo.md", "hash": compute_hash(content)}],
        "catalog_version": "",
        "has_incomplete_sync": False,
    }, state_file)


def test_update_no_changes_exits_0(tmp_path):
    remote = tmp_path / "remote"
    make_git_repo(remote)
    clone = tmp_path / "clone"
    subprocess.run(["git", "clone", str(remote), str(clone)], check=True, capture_output=True)

    dest_dir = tmp_path / "claude"
    state_file = tmp_path / ".state.json"
    setup_installed(dest_dir, state_file)

    code, output = run_update(clone, dest_dir, state_file)
    assert code == 0


def test_update_no_changes_reports_up_to_date(tmp_path):
    remote = tmp_path / "remote"
    make_git_repo(remote)
    clone = tmp_path / "clone"
    subprocess.run(["git", "clone", str(remote), str(clone)], check=True, capture_output=True)

    dest_dir = tmp_path / "claude"
    state_file = tmp_path / ".state.json"
    setup_installed(dest_dir, state_file)

    code, output = run_update(clone, dest_dir, state_file)
    assert "al día" in output or "sin cambios" in output.lower() or "unchanged" in output.lower()


def test_update_applies_changes_after_confirm(tmp_path):
    remote = tmp_path / "remote"
    make_git_repo(remote, catalog_content="# Updated content")
    clone = tmp_path / "clone"
    subprocess.run(["git", "clone", str(remote), str(clone)], check=True, capture_output=True)

    dest_dir = tmp_path / "claude"
    state_file = tmp_path / ".state.json"
    setup_installed(dest_dir, state_file, content="# Old content")

    code, _ = run_update(clone, dest_dir, state_file, stdin_text="s\n")
    assert code == 0
    assert (dest_dir / "commands" / "foo.md").read_text() == "# Updated content"


def test_update_cancel_does_not_apply(tmp_path):
    remote = tmp_path / "remote"
    make_git_repo(remote, catalog_content="# Updated content")
    clone = tmp_path / "clone"
    subprocess.run(["git", "clone", str(remote), str(clone)], check=True, capture_output=True)

    dest_dir = tmp_path / "claude"
    state_file = tmp_path / ".state.json"
    setup_installed(dest_dir, state_file, content="# Old content")

    code, _ = run_update(clone, dest_dir, state_file, stdin_text="n\n")
    assert code == 2
    assert (dest_dir / "commands" / "foo.md").read_text() == "# Old content"
