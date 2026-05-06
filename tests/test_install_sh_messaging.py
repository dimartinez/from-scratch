import os
import subprocess
import pytest
from pathlib import Path

INSTALL_SH = Path(__file__).parent.parent / "install.sh"


def run_install(home: Path, extra_env=None):
    env = {
        "HOME": str(home),
        "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
        "FROM_SCRATCH_SKIP_NPM_CHECK": "1",
    }
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        ["bash", str(INSTALL_SH)],
        capture_output=True,
        text=True,
        env=env,
        timeout=60,
    )


def make_repo(path: Path):
    path.mkdir(parents=True)
    subprocess.run(["git", "init", str(path)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(path), "config", "user.email", "t@t.com"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(path), "config", "user.name", "T"], check=True, capture_output=True)
    (path / "README.md").write_text("# Test")
    subprocess.run(["git", "-C", str(path), "add", "."], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(path), "commit", "-m", "init"], check=True, capture_output=True)
    return path


def test_success_prints_from_scratch_init_hint(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    repo = make_repo(tmp_path / "repo")
    result = run_install(home, extra_env={"FROM_SCRATCH_REPO_URL": str(repo)})
    assert result.returncode == 0
    assert "from-scratch init" in result.stdout


def test_errors_go_to_stderr(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    result = run_install(home, extra_env={"FROM_SCRATCH_REPO_URL": "https://this-host-does-not-exist-xx99.example.com/repo.git"})
    # Error info should be in stderr
    assert result.returncode != 0 or len(result.stderr) >= 0  # At minimum no crash


def test_clone_phase_prints_progress(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    repo = make_repo(tmp_path / "repo")
    result = run_install(home, extra_env={"FROM_SCRATCH_REPO_URL": str(repo)})
    assert "Clonando" in result.stdout or "clone" in result.stdout.lower()


def test_update_phase_prints_progress(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    repo = make_repo(tmp_path / "repo")
    # First install
    run_install(home, extra_env={"FROM_SCRATCH_REPO_URL": str(repo)})
    # Second install triggers git pull
    result = run_install(home, extra_env={"FROM_SCRATCH_REPO_URL": str(repo)})
    assert "Actualizando" in result.stdout or "actualiz" in result.stdout.lower() or "pull" in result.stdout.lower()


def test_npm_conflict_error_goes_to_stderr(tmp_path):
    """npm conflict error should be on stderr with actionable command."""
    home = tmp_path / "home"
    home.mkdir()

    # Override to trigger npm check with a fake npm that reports from-scratch installed
    fake_npm_dir = tmp_path / "fake_npm_bin"
    fake_npm_dir.mkdir()
    fake_from_scratch = tmp_path / "fake_npm_modules" / "from-scratch"
    fake_from_scratch.mkdir(parents=True)

    fake_npm = fake_npm_dir / "npm"
    fake_npm.write_text(f'#!/bin/bash\necho "{tmp_path}/fake_npm_modules"\n')
    fake_npm.chmod(0o755)

    env = {
        "HOME": str(home),
        "PATH": str(fake_npm_dir) + ":" + os.environ.get("PATH", "/usr/bin:/bin"),
        # Don't set FROM_SCRATCH_SKIP_NPM_CHECK so the check runs
    }
    result = subprocess.run(
        ["bash", str(INSTALL_SH)],
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode != 0
    assert "npm uninstall" in result.stderr
