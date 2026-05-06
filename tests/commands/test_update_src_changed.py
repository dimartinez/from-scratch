import io
import json
import subprocess
from pathlib import Path


def make_remote_with_src(tmp_path, catalog_content="# Foo", src_content="# v1"):
    remote = tmp_path / "remote"
    remote.mkdir(parents=True)
    (remote / "catalog").mkdir()
    (remote / "catalog" / "catalog.json").write_text(
        json.dumps({"entries": [{"kind": "command", "source": "commands/foo.md"}]})
    )
    (remote / "catalog" / "commands").mkdir()
    (remote / "catalog" / "commands" / "foo.md").write_text(catalog_content)
    (remote / "src").mkdir()
    (remote / "src" / "cli.py").write_text(src_content)
    subprocess.run(["git", "init", str(remote)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(remote), "config", "user.email", "t@t.com"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(remote), "config", "user.name", "T"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(remote), "add", "."], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(remote), "commit", "-m", "init"], check=True, capture_output=True)
    clone = tmp_path / "clone"
    subprocess.run(["git", "clone", str(remote), str(clone)], check=True, capture_output=True)
    return remote, clone


def test_src_change_only_prints_cli_update_notice(tmp_path):
    from src.commands.update import run_update
    from src.state.state import compute_hash, write_state

    remote, clone = make_remote_with_src(tmp_path)
    dest_dir = tmp_path / "claude"
    state_file = tmp_path / ".state.json"

    (dest_dir / "commands").mkdir(parents=True)
    (dest_dir / "commands" / "foo.md").write_text("# Foo")
    write_state({
        "last_sync_started_at": "2026-01-15T10:00:00Z",
        "last_sync_completed_at": "2026-01-15T10:00:00Z",
        "installed_files": [{"path": "commands/foo.md", "hash": compute_hash("# Foo")}],
        "catalog_version": "",
        "has_incomplete_sync": False,
    }, state_file)

    # Push a commit that only touches src/, not catalog/
    (remote / "src" / "cli.py").write_text("# v2")
    subprocess.run(["git", "-C", str(remote), "add", "src/cli.py"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(remote), "commit", "-m", "new command"], check=True, capture_output=True)

    out = io.StringIO()
    result = run_update(clone_dir=clone, dest_dir=dest_dir, state_path=state_file, out=out)

    output = out.getvalue()
    assert result == 0
    assert "El código de la CLI fue actualizado" in output
    assert "Todo al día" in output
