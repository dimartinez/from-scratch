import subprocess
import pytest
from pathlib import Path


def make_repo(path: Path) -> None:
    """Create a bare-minimum git repo with one commit."""
    subprocess.run(["git", "init", str(path)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(path), "config", "user.email", "test@test.com"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(path), "config", "user.name", "Test"], check=True, capture_output=True)
    (path / "file.txt").write_text("initial")
    subprocess.run(["git", "-C", str(path), "add", "."], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(path), "commit", "-m", "init"], check=True, capture_output=True)


def test_clone_repo_creates_clone(tmp_path):
    from src.sync.git import clone_repo
    remote = tmp_path / "remote"
    make_repo(remote)
    dest = tmp_path / "clone"
    clone_repo(str(remote), dest)
    assert (dest / "file.txt").exists()


def test_pull_ff_only_no_changes(tmp_path):
    from src.sync.git import clone_repo, pull_ff_only
    remote = tmp_path / "remote"
    make_repo(remote)
    dest = tmp_path / "clone"
    clone_repo(str(remote), dest)
    result = pull_ff_only(dest)
    assert result["changed_files"] == []


def test_pull_ff_only_with_new_commits(tmp_path):
    from src.sync.git import clone_repo, pull_ff_only
    remote = tmp_path / "remote"
    make_repo(remote)
    dest = tmp_path / "clone"
    clone_repo(str(remote), dest)

    # Add commit to remote
    (remote / "catalog" / "new.md").parent.mkdir(parents=True, exist_ok=True)
    (remote / "catalog" / "new.md").write_text("new content")
    subprocess.run(["git", "-C", str(remote), "add", "."], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(remote), "commit", "-m", "add new"], check=True, capture_output=True)

    result = pull_ff_only(dest)
    assert any("catalog/new.md" in f for f in result["changed_files"])


def test_pull_ff_only_fails_with_git_fast_forward_error(tmp_path):
    from src.sync.git import clone_repo, pull_ff_only
    from src.errors import GitFastForwardError

    remote = tmp_path / "remote"
    make_repo(remote)
    dest = tmp_path / "clone"
    clone_repo(str(remote), dest)

    # Add commit to remote
    (remote / "extra.txt").write_text("remote change")
    subprocess.run(["git", "-C", str(remote), "add", "."], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(remote), "commit", "-m", "remote commit"], check=True, capture_output=True)

    # Make local clone dirty (uncommitted change)
    (dest / "local_change.txt").write_text("local change")
    subprocess.run(["git", "-C", str(dest), "add", "."], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(dest), "commit", "-m", "local commit"], check=True, capture_output=True)

    with pytest.raises(GitFastForwardError):
        pull_ff_only(dest)


def test_pull_result_detects_src_changes(tmp_path):
    from src.sync.git import clone_repo, pull_ff_only
    remote = tmp_path / "remote"
    make_repo(remote)
    dest = tmp_path / "clone"
    clone_repo(str(remote), dest)

    (remote / "src" / "cli.py").parent.mkdir(parents=True, exist_ok=True)
    (remote / "src" / "cli.py").write_text("# updated")
    subprocess.run(["git", "-C", str(remote), "add", "."], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(remote), "commit", "-m", "update src"], check=True, capture_output=True)

    result = pull_ff_only(dest)
    assert result["src_changed"] is True


def test_pull_result_no_src_changes_when_only_catalog(tmp_path):
    from src.sync.git import clone_repo, pull_ff_only
    remote = tmp_path / "remote"
    make_repo(remote)
    dest = tmp_path / "clone"
    clone_repo(str(remote), dest)

    (remote / "catalog" / "foo.md").parent.mkdir(parents=True, exist_ok=True)
    (remote / "catalog" / "foo.md").write_text("new catalog entry")
    subprocess.run(["git", "-C", str(remote), "add", "."], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(remote), "commit", "-m", "catalog only"], check=True, capture_output=True)

    result = pull_ff_only(dest)
    assert result["src_changed"] is False
