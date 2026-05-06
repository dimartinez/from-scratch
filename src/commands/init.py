import sys
from datetime import datetime, timezone
from pathlib import Path

from src.catalog.manifest import parse_manifest
from src.sync.copy import copy_file, cleanup_orphan_tmp_files
from src.sync.diff import compute_diff
from src.state.state import read_state, write_state, compute_hash, has_incomplete_sync
from src.ui.preview import show_preview
from src.ui.hints import print_hint


def _load_catalog_entries(catalog_dir: Path) -> list:
    manifest_path = catalog_dir / "catalog.json"
    raw_entries = parse_manifest(manifest_path)
    entries = []
    for entry in raw_entries:
        source_path = catalog_dir / entry["source"]
        content = source_path.read_text(encoding="utf-8")
        entries.append({"path": entry["source"], "content": content})
    return entries


def run_init(
    catalog_dir: Path = None,
    dest_dir: Path = None,
    state_path: Path = None,
    force: bool = False,
    out=None,
    stdin=None,
) -> int:
    if out is None:
        out = sys.stdout
    if catalog_dir is None:
        catalog_dir = Path.home() / ".from-scratch" / "catalog"
    if dest_dir is None:
        dest_dir = Path.home() / ".claude"
    if state_path is None:
        state_path = Path.home() / ".claude" / "from-scratch" / ".state.json"

    cleanup_orphan_tmp_files(dest_dir)

    state = read_state(state_path)

    # Idempotence: already fully installed
    if not force and state and not has_incomplete_sync(state) and state.get("installed_files"):
        print_hint("already_initialized", out=out)
        return 0

    catalog_entries = _load_catalog_entries(catalog_dir)
    installed_files = state.get("installed_files", []) if state else []

    diff = compute_diff(catalog_entries, installed_files, dest_dir)

    # Abort if there are unowned conflicts and not --force
    if not force and diff["unowned_conflict"]:
        print("ERROR: Hay archivos en conflicto que from-scratch no instaló:", file=sys.stderr)
        for entry in diff["unowned_conflict"]:
            print(f"  ! {entry['path']}", file=sys.stderr)
        print("Usá --force para sobreescribir con backup.", file=sys.stderr)
        return 1

    # Build backup plan
    backups = []
    if force:
        for entry in diff.get("unchanged", []) + diff.get("modified", []) + diff.get("unowned_conflict", []):
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

    # Apply changes
    installed_by_path = {f["path"]: f for f in installed_files}
    new_installed = list(installed_files)

    to_install = diff["added"] + diff["modified"]
    if force:
        to_install += diff["unchanged"] + diff["unowned_conflict"]

    for entry in to_install:
        dest_file = dest_dir / entry["path"]
        needs_backup = dest_file.exists()
        copy_file(entry["content"], dest_file, backup=(force and needs_backup))
        file_hash = compute_hash(entry["content"])
        # Update or add to installed list
        existing = installed_by_path.get(entry["path"])
        if existing:
            existing["hash"] = file_hash
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

    print_hint("init_success", out=out)
    return 0
