---
name: fs-atomic-writes
description: >
  Every write under ~/.claude/ or to .state.json must use temp + os.rename, with optional .bak.{ms_timestamp} backup and orphan .tmp.{pid} cleanup.
  Trigger: When code writes to disk in src/sync/, src/state/, or anywhere it touches user-owned files.
metadata:
  version: '1.0.0'
---

## When to Use

Use this skill when:

- Writing files under `~/.claude/` or any user-owned destination.
- Editing `src/sync/copy.py` or `src/state/state.py`.
- Adding a new write path for any artifact the CLI manages (e.g., a future cache or lockfile).
- A test under `tests/sync/` is failing on partial writes or orphan tmp files.

---

## Critical Patterns

### Pattern 1: temp + rename is non-negotiable

The canonical pattern lives in `src/sync/copy.py::_atomic_write` and `src/state/state.py::write_state`:

```python
tmp = dest.parent / f"{dest.name}.tmp.{os.getpid()}"
try:
    tmp.write_text(content, encoding="utf-8")
    os.rename(tmp, dest)
except Exception:
    tmp.unlink(missing_ok=True)
    raise
```

`os.rename` is atomic on POSIX within the same filesystem. Writing directly to `dest` (no temp) is forbidden — a crash mid-write leaves a half-written file users will trust.

### Pattern 2: Always include `os.getpid()` in the tmp name

Concurrent runs of `from-scratch` would collide on the same `dest.tmp` and clobber each other. The PID suffix isolates them.

### Pattern 3: On failure, unlink the tmp

Use `tmp.unlink(missing_ok=True)` (Python 3.8+). If the rename fails, leaving the tmp behind would only be useful if the next run cleans it — which it does (Pattern 4) — but cleaning up locally keeps the FS tidy and avoids an extra warning.

### Pattern 4: Sweep orphan tmp files at sync entry

`cleanup_orphan_tmp_files(dest_base)` in `src/sync/copy.py` rglobs for `*.tmp.\d+$` and unlinks them. Call it before mutating anything so a previous crashed run does not leave landmines.

### Pattern 5: Backups use `.bak.{ms_timestamp}`, not `.bak`

When `backup=True`, the existing file is copied to `<name><suffix>.bak.<unix_ms>`. Multiple backups co-exist; nothing is overwritten. The user can `ls *.bak.*` and pick the one they want.

### Pattern 6: `mkdir(parents=True, exist_ok=True)` before writing

`copy_file` does it; new write paths must do it too. Otherwise the rename fails silently in CI but works on a developer machine where the parent already exists.

---

## Decision Tree

```
Need to update an existing file the user might have edited?  → backup=True, atomic write
Need to update an internal CLI file (.state.json)?           → atomic write, no backup
Need to delete a file the CLI installed?                     → unlink (no backup needed if recorded in state)
Need to write to /tmp or a scratch dir?                      → atomic still preferred, but not load-bearing
```

---

## Code Examples

### Example 1: Use the existing helper, don't reinvent

```python
from src.sync.copy import copy_file

copy_file(content="...", dest=Path("~/.claude/foo/bar.md").expanduser(), backup=True)
```

### Example 2: Adding a new managed file

If you must write somewhere `copy_file` does not cover (e.g. a binary format), follow the same shape:

```python
def write_lockfile(data: bytes, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.parent / f"{dest.name}.tmp.{os.getpid()}"
    try:
        tmp.write_bytes(data)
        os.rename(tmp, dest)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise
```

### Example 3: Sweep on entry

```python
from src.sync.copy import cleanup_orphan_tmp_files
removed = cleanup_orphan_tmp_files(dest_base)
if removed:
    print_hint("orphan_tmp_cleaned", count=removed)  # add the hint key in src/ui/hints.py
```

---

## Commands

```bash
# Run the atomicity tests
python -m pytest tests/sync/ -k "atomic or orphan or backup"

# Inspect the live install for tmp leftovers
find ~/.claude/from-scratch -name '*.tmp.*'
```

---

## Resources

- **Source**: [src/sync/copy.py](../../src/sync/copy.py), [src/state/state.py](../../src/state/state.py)
- **Tests**: [tests/sync/](../../tests/sync/)
- **Related skills**: `fs-state-sync` (when to backup vs overwrite), `fs-error-contract` (rename failures must surface as `FromScratchError`).
