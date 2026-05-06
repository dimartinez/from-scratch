import io
import json
from pathlib import Path
import pytest


# ---------------------------------------------------------------------------
# 1. Bootstrap helper
# ---------------------------------------------------------------------------

def make_installed_env(tmp_path):
    """
    Creates a realistic installed environment under tmp_path.

    Catalog files:
      dest_dir/commands/new-project.md
      dest_dir/commands/from-scratch/sync-skills.md

    State file:
      dest_dir/from-scratch/.state.json  (lists both files above)

    Tool dir and wrapper:
      tool_dir/  (tmp_path/tool/)
      wrapper_path  (tmp_path/bin/from-scratch)

    Returns a dict with dest_dir, state_path, tool_dir, wrapper_path.
    """
    dest_dir = tmp_path / "claude"
    state_path = dest_dir / "from-scratch" / ".state.json"
    tool_dir = tmp_path / "tool"
    wrapper_path = tmp_path / "bin" / "from-scratch"

    # Catalog files
    (dest_dir / "commands").mkdir(parents=True)
    (dest_dir / "commands" / "new-project.md").write_text("# new-project")
    (dest_dir / "commands" / "from-scratch").mkdir()
    (dest_dir / "commands" / "from-scratch" / "sync-skills.md").write_text("# sync-skills")

    # State file
    state_path.parent.mkdir(parents=True)
    state = {
        "installed_files": [
            {"path": "commands/new-project.md", "hash": "abc"},
            {"path": "commands/from-scratch/sync-skills.md", "hash": "def"},
        ],
        "last_sync_started_at": "2026-01-01T00:00:00+00:00",
        "last_sync_completed_at": "2026-01-01T00:00:00+00:00",
        "catalog_version": "",
        "has_incomplete_sync": False,
    }
    state_path.write_text(json.dumps(state))

    # Tool dir and wrapper
    tool_dir.mkdir(parents=True)
    (tool_dir / "src").mkdir()
    wrapper_path.parent.mkdir(parents=True)
    wrapper_path.write_text("#!/bin/bash\nexec python3 ~/.from-scratch/src/cli.py")

    return {
        "dest_dir": dest_dir,
        "state_path": state_path,
        "tool_dir": tool_dir,
        "wrapper_path": wrapper_path,
    }


def _run(env, stdin_text="s\n"):
    from src.commands.uninstall import run_uninstall
    out = io.StringIO()
    stdin = io.StringIO(stdin_text)
    code = run_uninstall(
        dest_dir=env["dest_dir"],
        state_path=env["state_path"],
        tool_dir=env["tool_dir"],
        wrapper_path=env["wrapper_path"],
        out=out,
        stdin=stdin,
    )
    return code, out.getvalue()


# ---------------------------------------------------------------------------
# 2. Mensajes UI — render_uninstall_preview
# ---------------------------------------------------------------------------

def test_render_uninstall_preview_contains_count_and_paths():
    from src.ui.preview import render_uninstall_preview

    files = [Path("/home/user/.claude/commands/new-project.md")]
    dirs = [Path("/home/user/.claude/commands/from-scratch")]
    state_dir = Path("/home/user/.claude/from-scratch")
    tool_dir = Path("/home/user/.from-scratch")
    wrapper = Path("/home/user/.local/bin/from-scratch")

    result = render_uninstall_preview(
        files=files,
        dirs=dirs,
        state_dir=state_dir,
        tool_dir=tool_dir,
        wrapper=wrapper,
    )

    assert "(1)" in result
    assert str(state_dir) in result
    assert str(tool_dir) in result
    assert str(wrapper) in result


# ---------------------------------------------------------------------------
# 2. Mensajes UI — hints
# ---------------------------------------------------------------------------

def test_hints_contain_init_suggestion():
    from src.ui.hints import print_hint

    for name in ("already_uninstalled", "uninstall_success"):
        out = io.StringIO()
        print_hint(name, out=out)
        assert "from-scratch init" in out.getvalue(), (
            f"hint '{name}' debería contener 'from-scratch init'"
        )


def test_uninstall_cancelled_hint_is_defined():
    from src.ui.hints import print_hint

    out = io.StringIO()
    print_hint("uninstall_cancelled", out=out)
    assert out.getvalue().strip() != ""


# ---------------------------------------------------------------------------
# 2. Mensajes UI — UninstallPermissionError
# ---------------------------------------------------------------------------

def test_uninstall_permission_error_attributes():
    from src.errors import UninstallPermissionError

    err = UninstallPermissionError("/some/path")
    assert err.code == "UNINSTALL_PERMISSION_ERROR"
    assert "sudo rm" in err.remediation


# ---------------------------------------------------------------------------
# 3. run_uninstall — estado ausente y state corrupto
# ---------------------------------------------------------------------------

def test_no_state_returns_0_with_hint(tmp_path):
    env = make_installed_env(tmp_path)
    env["state_path"].unlink()

    out = io.StringIO()
    stdin = io.StringIO()
    from src.commands.uninstall import run_uninstall
    code = run_uninstall(
        dest_dir=env["dest_dir"],
        state_path=env["state_path"],
        tool_dir=env["tool_dir"],
        wrapper_path=env["wrapper_path"],
        out=out,
        stdin=stdin,
    )

    assert code == 0
    assert "from-scratch init" in out.getvalue()


def test_corrupt_state_returns_1_without_deleting(tmp_path):
    env = make_installed_env(tmp_path)
    env["state_path"].write_text("{")

    catalog_file = env["dest_dir"] / "commands" / "new-project.md"
    assert catalog_file.exists()

    code, _ = _run(env, stdin_text="s\n")

    assert code == 1
    assert catalog_file.exists()


# ---------------------------------------------------------------------------
# 4. run_uninstall — confirmación interactiva
# ---------------------------------------------------------------------------

def test_preview_contains_count_and_paths(tmp_path):
    env = make_installed_env(tmp_path)
    out = io.StringIO()
    stdin = io.StringIO("n\n")
    from src.commands.uninstall import run_uninstall
    run_uninstall(
        dest_dir=env["dest_dir"],
        state_path=env["state_path"],
        tool_dir=env["tool_dir"],
        wrapper_path=env["wrapper_path"],
        out=out,
        stdin=stdin,
    )
    output = out.getvalue()

    assert "(2)" in output
    assert str(env["tool_dir"]) in output
    assert str(env["wrapper_path"]) in output


def test_cancel_returns_2_without_deleting(tmp_path):
    env = make_installed_env(tmp_path)
    catalog_file = env["dest_dir"] / "commands" / "new-project.md"

    code, _ = _run(env, stdin_text="n\n")

    assert code == 2
    assert catalog_file.exists()


# ---------------------------------------------------------------------------
# 5. run_uninstall — borrado de archivos del catálogo
# ---------------------------------------------------------------------------

def test_confirmed_deletes_all_catalog_files(tmp_path):
    env = make_installed_env(tmp_path)
    code, _ = _run(env, stdin_text="s\n")

    assert code == 0
    assert not (env["dest_dir"] / "commands" / "new-project.md").exists()
    assert not (env["dest_dir"] / "commands" / "from-scratch" / "sync-skills.md").exists()


def test_missing_catalog_file_does_not_abort(tmp_path):
    env = make_installed_env(tmp_path)
    (env["dest_dir"] / "commands" / "new-project.md").unlink()

    code, _ = _run(env, stdin_text="s\n")

    assert code == 0


# ---------------------------------------------------------------------------
# 6. run_uninstall — limpieza de directorios vacíos
# ---------------------------------------------------------------------------

def test_empty_parent_dirs_are_removed(tmp_path):
    env = make_installed_env(tmp_path)
    _run(env, stdin_text="s\n")

    assert not (env["dest_dir"] / "commands" / "from-scratch").exists()


def test_non_empty_dir_is_kept(tmp_path):
    env = make_installed_env(tmp_path)
    extra = env["dest_dir"] / "commands" / "from-scratch" / "user-file.md"
    extra.write_text("# user content")

    _run(env, stdin_text="s\n")

    assert (env["dest_dir"] / "commands" / "from-scratch").exists()


def test_unrelated_dir_is_kept(tmp_path):
    env = make_installed_env(tmp_path)
    unrelated = env["dest_dir"] / "my-own-dir"
    unrelated.mkdir()

    _run(env, stdin_text="s\n")

    assert unrelated.exists()


# ---------------------------------------------------------------------------
# 7. run_uninstall — state dir, tool dir, wrapper
# ---------------------------------------------------------------------------

def test_state_dir_is_deleted(tmp_path):
    env = make_installed_env(tmp_path)
    _run(env, stdin_text="s\n")

    assert not env["state_path"].parent.exists()


def test_tool_dir_and_wrapper_are_deleted(tmp_path):
    env = make_installed_env(tmp_path)
    _run(env, stdin_text="s\n")

    assert not env["tool_dir"].exists()
    assert not env["wrapper_path"].exists()


def test_permission_error_on_file_does_not_abort(tmp_path, monkeypatch):
    env = make_installed_env(tmp_path)
    first_file = env["dest_dir"] / "commands" / "new-project.md"
    original_unlink = Path.unlink

    def mock_unlink(self, missing_ok=False):
        if self == first_file:
            raise PermissionError("permission denied")
        original_unlink(self, missing_ok=missing_ok)

    monkeypatch.setattr(Path, "unlink", mock_unlink)

    code, output = _run(env, stdin_text="s\n")

    assert not (env["dest_dir"] / "commands" / "from-scratch" / "sync-skills.md").exists()
    assert str(first_file) in output
    assert "sudo rm" in output


def test_permission_error_returns_exit_code_1(tmp_path, monkeypatch):
    env = make_installed_env(tmp_path)
    first_file = env["dest_dir"] / "commands" / "new-project.md"
    original_unlink = Path.unlink

    def mock_unlink(self, missing_ok=False):
        if self == first_file:
            raise PermissionError("permission denied")
        original_unlink(self, missing_ok=missing_ok)

    monkeypatch.setattr(Path, "unlink", mock_unlink)

    code, _ = _run(env, stdin_text="s\n")

    assert code == 1


def test_success_returns_0_with_hint(tmp_path):
    env = make_installed_env(tmp_path)
    code, output = _run(env, stdin_text="s\n")

    assert code == 0
    assert "from-scratch init" in output


# ---------------------------------------------------------------------------
# 8. Integración CLI
# ---------------------------------------------------------------------------

def test_main_dispatches_to_run_uninstall(monkeypatch):
    import src.commands.uninstall
    calls = []

    def mock_run_uninstall(**kwargs):
        calls.append(kwargs)
        return 0

    monkeypatch.setattr(src.commands.uninstall, "run_uninstall", mock_run_uninstall)

    from src.cli import main
    exit_code = main(["uninstall"])

    assert len(calls) == 1
    assert exit_code == 0


# ---------------------------------------------------------------------------
# 9. Test de aceptación end-to-end
# ---------------------------------------------------------------------------

def test_acceptance_full_uninstall(tmp_path):
    env = make_installed_env(tmp_path)
    code, output = _run(env, stdin_text="s\n")

    assert code == 0
    assert not (env["dest_dir"] / "commands" / "new-project.md").exists()
    assert not (env["dest_dir"] / "commands" / "from-scratch" / "sync-skills.md").exists()
    assert not env["state_path"].parent.exists()
    assert not env["tool_dir"].exists()
    assert not env["wrapper_path"].exists()
    assert "from-scratch init" in output
