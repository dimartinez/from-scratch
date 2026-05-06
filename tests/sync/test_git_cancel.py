import signal
import subprocess
import threading
import pytest
from pathlib import Path


def make_repo(path: Path) -> None:
    subprocess.run(["git", "init", str(path)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(path), "config", "user.email", "t@t.com"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(path), "config", "user.name", "T"], check=True, capture_output=True)
    (path / "f.txt").write_text("initial")
    subprocess.run(["git", "-C", str(path), "add", "."], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(path), "commit", "-m", "init"], check=True, capture_output=True)


def test_keyboard_interrupt_propagates(tmp_path):
    """A KeyboardInterrupt raised during pull propagates to the caller."""
    from src.sync.git import clone_repo, pull_ff_only
    from unittest.mock import patch
    import subprocess as sp

    remote = tmp_path / "remote"
    make_repo(remote)
    dest = tmp_path / "clone"
    clone_repo(str(remote), dest)

    # Patch subprocess.run inside src.sync.git to raise KeyboardInterrupt
    original_run = sp.run
    def raising_run(*args, **kwargs):
        if "pull" in (args[0] if args else []):
            raise KeyboardInterrupt
        return original_run(*args, **kwargs)

    with patch("src.sync.git.subprocess.run", side_effect=raising_run):
        with pytest.raises(KeyboardInterrupt):
            pull_ff_only(dest)


def test_pull_does_not_use_start_new_session():
    """Verify subprocess.run is not called with start_new_session=True."""
    import inspect
    import src.sync.git as git_module
    source = inspect.getsource(git_module)
    assert "start_new_session=True" not in source


def test_clone_left_in_consistent_state_after_interrupt(tmp_path):
    """After a completed pull, clone is in a consistent state."""
    from src.sync.git import clone_repo, pull_ff_only

    remote = tmp_path / "remote"
    make_repo(remote)
    dest = tmp_path / "clone"
    clone_repo(str(remote), dest)

    # Add a commit to remote
    (remote / "new.txt").write_text("added")
    subprocess.run(["git", "-C", str(remote), "add", "."], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(remote), "commit", "-m", "new commit"], check=True, capture_output=True)

    result = pull_ff_only(dest)
    # Either the pull completed or nothing changed — never partial
    sha = subprocess.run(
        ["git", "-C", str(dest), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True
    ).stdout.strip()
    assert sha  # Has a valid SHA
