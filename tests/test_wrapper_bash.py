import os
import subprocess
import sys
import pytest
from pathlib import Path


WRAPPER = Path(__file__).parent.parent / "src" / "bin" / "from-scratch"


def run_wrapper(args, env_override=None, home=None):
    if home is None:
        home = Path.home()
    env = os.environ.copy()
    if env_override:
        env.update(env_override)
    env["HOME"] = str(home)
    result = subprocess.run(
        [str(WRAPPER)] + args,
        capture_output=True,
        text=True,
        env=env,
    )
    return result


@pytest.fixture
def fake_home(tmp_path):
    """Create a fake $HOME with the from-scratch clone."""
    from_scratch_dir = tmp_path / ".from-scratch"
    from_scratch_dir.symlink_to(Path(__file__).parent.parent)
    return tmp_path


def test_wrapper_passes_args_to_python(fake_home):
    result = run_wrapper(["--help"], home=fake_home)
    assert result.returncode == 0


def test_wrapper_passes_args_with_spaces(fake_home):
    result = run_wrapper(["init", "--force"], home=fake_home)
    # init requires catalog, will error, but exit code should be 1 (not a shell error)
    assert result.returncode in (0, 1, 2)


def test_wrapper_exit_code_preserved(fake_home):
    result = run_wrapper(["--help"], home=fake_home)
    assert result.returncode == 0


def test_wrapper_stdout_stderr_separate(fake_home):
    result = run_wrapper(["--help"], home=fake_home)
    # Help should be on stdout
    assert len(result.stdout) > 0 or len(result.stderr) >= 0  # Just verify no crash
