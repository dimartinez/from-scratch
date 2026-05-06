import hashlib
from pathlib import Path


def _sha256(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()


def compute_diff(catalog_entries: list, installed_files: list, dest_base: Path) -> dict:
    """Compare catalog state vs installed state and return categorized diff.

    catalog_entries: list of {"path": str, "content": str}
    installed_files: list of {"path": str, "hash": str}
    dest_base: Path prefix for installed files on disk
    """
    result = {
        "added": [],
        "modified": [],
        "unchanged": [],
        "removed": [],
        "user_modified": [],
        "unowned_conflict": [],
    }

    installed_by_path = {f["path"]: f for f in installed_files}
    catalog_paths = {e["path"] for e in catalog_entries}

    for entry in catalog_entries:
        path = entry["path"]
        content = entry["content"]
        catalog_hash = _sha256(content)
        dest_file = dest_base / path

        if path in installed_by_path:
            recorded_hash = installed_by_path[path]["hash"]
            disk_hash = _sha256(dest_file.read_text(encoding="utf-8")) if dest_file.exists() else None

            # Drift detection: disk differs from what we installed
            if disk_hash is not None and disk_hash != recorded_hash:
                result["user_modified"].append({
                    "path": path,
                    "has_remote_update": catalog_hash != recorded_hash,
                })
                continue

            if catalog_hash == recorded_hash:
                result["unchanged"].append({"path": path})
            else:
                result["modified"].append({"path": path, "content": content})
        else:
            # Not in our state file
            if dest_file.exists():
                result["unowned_conflict"].append({"path": path})
            else:
                result["added"].append({"path": path, "content": content})

    # Find removed: in installed but not in catalog anymore
    for installed in installed_files:
        if installed["path"] not in catalog_paths:
            result["removed"].append({"path": installed["path"]})

    return result
