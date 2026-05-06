import subprocess
import pytest
from pathlib import Path


def make_repo(path: Path) -> None:
    subprocess.run(["git", "init", str(path)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(path), "config", "user.email", "t@t.com"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(path), "config", "user.name", "T"], check=True, capture_output=True)
    (path / "f.txt").write_text("x")
    subprocess.run(["git", "-C", str(path), "add", "."], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(path), "commit", "-m", "init"], check=True, capture_output=True)


def test_clone_bogus_url_raises_network_error(tmp_path):
    from src.sync.git import clone_repo
    from src.errors import NetworkError
    dest = tmp_path / "clone"
    with pytest.raises((NetworkError, RuntimeError)):
        clone_repo("https://this-host-does-not-exist-zz9.example.com/repo.git", dest)


def test_clone_bogus_url_does_not_leave_partial_dir(tmp_path):
    from src.sync.git import clone_repo
    from src.errors import NetworkError
    dest = tmp_path / "clone"
    try:
        clone_repo("https://this-host-does-not-exist-zz9.example.com/repo.git", dest)
    except (NetworkError, RuntimeError):
        pass
    assert not dest.exists()


def test_pull_unreachable_remote_raises_network_error(tmp_path):
    from src.sync.git import clone_repo, pull_ff_only
    from src.errors import NetworkError
    remote = tmp_path / "remote"
    make_repo(remote)
    dest = tmp_path / "clone"
    clone_repo(str(remote), dest)

    # Break the remote URL
    subprocess.run(
        ["git", "-C", str(dest), "remote", "set-url", "origin",
         "https://this-host-does-not-exist-zz9.example.com/repo.git"],
        check=True, capture_output=True
    )

    with pytest.raises((NetworkError, RuntimeError)):
        pull_ff_only(dest)


def test_pull_network_error_leaves_clone_intact(tmp_path):
    from src.sync.git import clone_repo, pull_ff_only
    from src.errors import NetworkError
    remote = tmp_path / "remote"
    make_repo(remote)
    dest = tmp_path / "clone"
    clone_repo(str(remote), dest)

    # Remember what files exist
    files_before = set(dest.iterdir())

    subprocess.run(
        ["git", "-C", str(dest), "remote", "set-url", "origin",
         "https://this-host-does-not-exist-zz9.example.com/repo.git"],
        check=True, capture_output=True
    )

    try:
        pull_ff_only(dest)
    except (NetworkError, RuntimeError):
        pass

    files_after = set(dest.iterdir())
    assert files_before == files_after
