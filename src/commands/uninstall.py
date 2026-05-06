import shutil
import sys
from pathlib import Path

from src.state.state import read_state
from src.errors import StateCorruptError
from src.ui.hints import print_hint
from src.ui.preview import render_uninstall_preview


def run_uninstall(
    dest_dir: Path = None,
    state_path: Path = None,
    tool_dir: Path = None,
    wrapper_path: Path = None,
    out=None,
    stdin=None,
) -> int:
    if out is None:
        out = sys.stdout
    if stdin is None:
        stdin = sys.stdin
    if dest_dir is None:
        dest_dir = Path.home() / ".claude"
    if state_path is None:
        state_path = Path.home() / ".claude" / "from-scratch" / ".state.json"
    if tool_dir is None:
        tool_dir = Path.home() / ".from-scratch"
    if wrapper_path is None:
        wrapper_path = Path.home() / ".local" / "bin" / "from-scratch"

    # Step 1: Read state
    try:
        state = read_state(state_path)
    except StateCorruptError as exc:
        print(f"ERROR: {exc.message}", file=out)
        print(f"Remediación: {exc.remediation}", file=out)
        return 1

    if state is None:
        print_hint("already_uninstalled", out=out)
        return 0

    installed_files = state.get("installed_files", [])
    candidate_dirs = _candidate_dirs(installed_files, dest_dir)

    # Step 2: Show preview and confirm
    preview = render_uninstall_preview(
        files=[dest_dir / f["path"] for f in installed_files],
        dirs=candidate_dirs,
        state_dir=state_path.parent,
        tool_dir=tool_dir,
        wrapper=wrapper_path,
    )
    print(preview, file=out, end="")
    answer = stdin.readline().strip()
    if answer not in ("s", "S"):
        print_hint("uninstall_cancelled", out=out)
        return 2

    # Step 3: Delete catalog files
    failed = []
    for entry in installed_files:
        file_path = dest_dir / entry["path"]
        try:
            file_path.unlink(missing_ok=True)
        except PermissionError:
            failed.append(("file", file_path))

    # Step 4: Clean empty dirs (only parents of installed_files, leaf to root)
    for d in sorted(candidate_dirs, key=lambda p: len(p.parts), reverse=True):
        if d == dest_dir:
            continue
        if d.exists() and not any(d.iterdir()):
            try:
                d.rmdir()
            except OSError:
                pass

    # Step 5: Delete state dir
    state_dir = state_path.parent
    if state_dir.exists():
        try:
            shutil.rmtree(state_dir)
        except PermissionError:
            failed.append(("dir", state_dir))

    # Step 6: Delete tool dir
    if tool_dir.exists():
        try:
            shutil.rmtree(tool_dir)
        except PermissionError:
            failed.append(("dir", tool_dir))

    # Step 7: Delete wrapper
    try:
        wrapper_path.unlink(missing_ok=True)
    except PermissionError:
        failed.append(("file", wrapper_path))

    # Step 8: Report result
    if failed:
        print("", file=out)
        print("No se pudieron eliminar los siguientes elementos:", file=out)
        for kind, path in failed:
            print(f"  No se pudo eliminar `{path}`: permiso denegado", file=out)
            if kind == "dir":
                print(f"  Remediación: sudo rm -rf {path}", file=out)
            else:
                print(f"  Remediación: sudo rm {path}", file=out)
        return 1

    print_hint("uninstall_success", out=out)
    return 0


def _candidate_dirs(installed_files: list, dest_dir: Path) -> list:
    seen = set()
    dirs = []
    for entry in installed_files:
        file_path = dest_dir / entry["path"]
        parent = file_path.parent
        while parent != dest_dir and parent not in seen:
            seen.add(parent)
            dirs.append(parent)
            parent = parent.parent
    return dirs
