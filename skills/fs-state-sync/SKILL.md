---
name: fs-state-sync
description: >
  Diff/state semantics for from-scratch — six diff categories and the role of .state.json with SHA256 hashes.
  Trigger: When editing src/sync/diff.py, src/state/state.py, or any code that reasons about what is "installed" vs "on disk".
metadata:
  version: '1.0.0'
---

## When to Use

Use this skill when:

- Modifying the diff algorithm (`src/sync/diff.py`).
- Adding fields to `~/.claude/from-scratch/.state.json`.
- Implementing a new sync command or changing the safety policy of an existing one.
- A user reports that their hand-edited file was overwritten or that an unrelated file was wiped.

---

## Critical Patterns

### Pattern 1: Hashes track "what the CLI installed", not "what is on disk"

`.state.json` records, per path, the SHA256 the CLI **wrote**. The current bytes on disk may differ — that is the **whole point** of drift detection.

```
recorded_hash → what CLI installed last
disk_hash     → bytes currently on the filesystem
catalog_hash  → bytes coming from the new catalog
```

### Pattern 2: Six diff categories — never invent a seventh

| Category           | Means                                            | Default action       |
| ------------------ | ------------------------------------------------ | -------------------- |
| `added`            | In catalog, not in state, not on disk            | Write file           |
| `modified`         | In catalog and state, catalog hash changed       | Overwrite            |
| `unchanged`        | catalog == state == disk                         | Skip                 |
| `removed`          | In state, no longer in catalog                   | Delete (with backup) |
| `user_modified`    | Tracked but disk drifted from `recorded_hash`    | **Skip** without `--force` |
| `unowned_conflict` | New entry; file already exists, not in state     | **Skip** without `--force` |

The last two are the safety contract: the CLI never silently overwrites user work or files it does not own.

### Pattern 3: `--force` is the only way to bypass the safety categories

Anywhere new code might overwrite, branch on `force` explicitly. Reviewers will look for it.

### Pattern 4: `has_incomplete_sync` is the recovery hook

`last_sync_started_at > last_sync_completed_at` ⇒ a previous run died mid-write. New sync code should detect this and tell the user (`incomplete_sync` hint) before proceeding.

---

## Decision Tree

```
File in state and disk hash == recorded?     → catalog vs recorded → unchanged | modified
File in state and disk hash != recorded?     → user_modified (skip unless --force)
File NOT in state and on disk?               → unowned_conflict (skip unless --force)
File NOT in state and NOT on disk?           → added
File in state but NOT in catalog?            → removed
```

---

## Code Examples

### Example 1: Reading state safely

```python
from src.state.state import read_state, default_state_path

state = read_state(default_state_path())
if state is None:
    # No file yet — first install. Do not raise.
    state = {"files": []}
```

`read_state` returns `None` for "absent", but raises `StateCorruptError` for invalid JSON, wrong type, or non-UTF-8 bytes. Do not collapse those into a generic catch.

### Example 2: Iterating diff results

```python
diff = compute_diff(catalog_entries, state.get("files", []), dest_base)
for entry in diff["user_modified"]:
    if not force:
        # Skipped on purpose. Tell the user.
        continue
    # ... overwrite path
```

---

## Commands

```bash
# Inspect the live state file
cat ~/.claude/from-scratch/.state.json | python -m json.tool

# Force a clean reinstall
rm ~/.claude/from-scratch/.state.json && from-scratch init

# Run only the diff/state tests
python -m pytest tests/sync/ tests/state/
```

---

## Resources

- **Source**: [src/sync/diff.py](../../src/sync/diff.py), [src/state/state.py](../../src/state/state.py)
- **Tests**: [tests/sync/](../../tests/sync/), [tests/state/](../../tests/state/)
- **Related skills**: `fs-atomic-writes` (how state file is persisted), `fs-error-contract` (`StateCorruptError`).
