import subprocess
from pathlib import Path


def clone_repo(url: str, dest: Path) -> None:
    from src.errors import NetworkError
    result = subprocess.run(
        ["git", "clone", url, str(dest)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        # Partial clone directory cleanup
        if dest.exists():
            import shutil
            shutil.rmtree(dest, ignore_errors=True)
        _raise_network_or_other(result, f"clone de {url}")


def pull_ff_only(repo: Path) -> dict:
    from src.errors import GitFastForwardError, NetworkError

    # Capture current HEAD before pull
    before = _current_sha(repo)

    result = subprocess.run(
        ["git", "-C", str(repo), "pull", "--ff-only"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        stderr = result.stderr.lower()
        if "not possible to fast-forward" in stderr or "cannot fast-forward" in stderr or "diverged" in stderr:
            raise GitFastForwardError()
        _raise_network_or_other(result, "pull --ff-only")

    after = _current_sha(repo)

    if before == after:
        return {"changed_files": [], "src_changed": False}

    # Get list of changed files between before and after
    diff = subprocess.run(
        ["git", "-C", str(repo), "diff", "--name-only", before, after],
        capture_output=True,
        text=True,
        check=True,
    )
    changed_files = [f for f in diff.stdout.splitlines() if f]
    src_changed = any(f.startswith("src/") for f in changed_files)

    return {"changed_files": changed_files, "src_changed": src_changed}


def _current_sha(repo: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def _raise_network_or_other(result: subprocess.CompletedProcess, context: str) -> None:
    from src.errors import NetworkError
    stderr = result.stderr.lower()
    network_indicators = [
        "could not resolve host",
        "network",
        "connection",
        "unable to connect",
        "ssl",
        "timeout",
        "repository not found",
        "fatal: repository",
        "error: failed to push",
    ]
    if any(indicator in stderr for indicator in network_indicators):
        raise NetworkError(f"Error de red durante {context}: {result.stderr.strip()}")
    raise RuntimeError(f"git {context} falló (exit {result.returncode}): {result.stderr.strip()}")
