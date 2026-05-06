import sys
from datetime import datetime, timezone
from pathlib import Path

from src.catalog.manifest import parse_manifest
from src.sync.copy import copy_file, cleanup_orphan_tmp_files
from src.sync.diff import compute_diff
from src.state.state import read_state, write_state, compute_hash, has_incomplete_sync
from src.ui.preview import show_preview
from src.ui.hints import print_hint


def _load_catalog_entries(clone_dir: Path) -> list:
    catalog_dir = clone_dir / "catalog"
    manifest_path = catalog_dir / "catalog.json"
    raw_entries = parse_manifest(manifest_path)
    entries = []
    for entry in raw_entries:
        source_path = catalog_dir / entry["source"]
        content = source_path.read_text(encoding="utf-8")
        entries.append({"path": entry["source"], "content": content})
    return entries


def run_update(
    clone_dir: Path = None,
    dest_dir: Path = None,
    state_path: Path = None,
    force: bool = False,
    out=None,
    stdin=None,
    skip_pull: bool = False,
) -> int:
    if out is None:
        out = sys.stdout
    if clone_dir is None:
        clone_dir = Path.home() / ".from-scratch"
    if dest_dir is None:
        dest_dir = Path.home() / ".claude"
    if state_path is None:
        state_path = Path.home() / ".claude" / "from-scratch" / ".state.json"

    cleanup_orphan_tmp_files(dest_dir)

    # Pull (unless skipped for testing)
    src_changed = False
    if not skip_pull:
        from src.sync.git import pull_ff_only
        pull_result = pull_ff_only(clone_dir)
        src_changed = pull_result.get("src_changed", False)

    catalog_entries = _load_catalog_entries(clone_dir)
    state = read_state(state_path)
    installed_files = state.get("installed_files", []) if state else []

    diff = compute_diff(catalog_entries, installed_files, dest_dir)

    # Check if everything is already up to date
    if not diff["added"] and not diff["modified"] and not diff["user_modified"] and not diff["unowned_conflict"] and not diff["removed"]:
        last_sync = state.get("last_sync_completed_at", "") if state else ""
        print_hint("update_no_changes", out=out, last_sync_at=last_sync)
        return 0

    # Handle user_modified: without force, skip them; with force, include them
    if not force and diff["user_modified"]:
        # Show them in preview as conflicts but don't include in install
        pass

    # Build backup plan
    backups = []
    if force:
        for entry in diff.get("user_modified", []):
            dest_file = dest_dir / entry["path"]
            if dest_file.exists():
                import time
                ts = int(time.time() * 1000)
                backup_path = dest_file.with_suffix(f"{dest_file.suffix}.bak.{ts}")
                backups.append((entry["path"], str(backup_path)))

    # Show preview and confirm
    confirmed = show_preview(diff, backups=backups, out=out, stdin=stdin)
    if not confirmed:
        return 2

    # Mark sync started
    now = datetime.now(timezone.utc).isoformat()
    new_state = {
        "last_sync_started_at": now,
        "last_sync_completed_at": None,
        "installed_files": installed_files[:],
        "catalog_version": "",
        "has_incomplete_sync": True,
    }
    write_state(new_state, state_path)

    installed_by_path = {f["path"]: f for f in installed_files}
    new_installed = list(installed_files)

    to_install = diff["added"] + diff["modified"]
    if force:
        # Also overwrite user_modified files
        for entry in diff.get("user_modified", []):
            # Find catalog content
            for ce in catalog_entries:
                if ce["path"] == entry["path"]:
                    to_install.append(ce)
                    break

    for entry in to_install:
        dest_file = dest_dir / entry["path"]
        needs_backup = dest_file.exists() and force
        copy_file(entry["content"], dest_file, backup=needs_backup)
        file_hash = compute_hash(entry["content"])
        existing = installed_by_path.get(entry["path"])
        if existing:
            existing["hash"] = file_hash
            for item in new_installed:
                if item["path"] == entry["path"]:
                    item["hash"] = file_hash
                    break
        else:
            new_installed.append({"path": entry["path"], "hash": file_hash})

    # Write final state
    final_state = {
        "last_sync_started_at": now,
        "last_sync_completed_at": datetime.now(timezone.utc).isoformat(),
        "installed_files": new_installed,
        "catalog_version": "",
        "has_incomplete_sync": False,
    }
    write_state(final_state, state_path)

    if src_changed:
        print("-> El código de la CLI fue actualizado. La próxima ejecución usará la versión nueva.", file=out)

    return 0
