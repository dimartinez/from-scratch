---
name: fs-install-wrapper
description: >
  The `from-scratch` binary is generated dynamically by install.sh in ~/.local/bin and exports PYTHONPATH=$HOME/.from-scratch. Layout changes break it.
  Trigger: When editing install.sh, moving files under src/, adding entry-points, or debugging a "command not found" / "module not found" report.
metadata:
  version: '1.0.0'
---

## When to Use

Use this skill when:

- Editing [install.sh](../../install.sh).
- Moving, renaming, or deleting any file at the top of `src/` (especially `src/cli.py`).
- Adding a new CLI entry-point.
- A user reports `from-scratch: command not found` or `ModuleNotFoundError: No module named 'src'`.

---

## Critical Patterns

### Pattern 1: The wrapper is generated, never versioned

`install.sh` writes `~/.local/bin/from-scratch` as a 4-line bash heredoc:

```bash
#!/usr/bin/env bash
export PYTHONPATH="$HOME/.from-scratch${PYTHONPATH:+:$PYTHONPATH}"
exec python3 "$HOME/.from-scratch/src/cli.py" "$@"
```

Two invariants follow:

1. The Python entry-point **must remain at `src/cli.py`**. Renaming or moving it breaks every existing install — and there is no upgrade path other than re-running `install.sh`.
2. All imports inside the project **must be absolute, rooted at `src.`** (`from src.errors import ...`). This is why `PYTHONPATH=$HOME/.from-scratch` (the parent of `src/`) is exported.

### Pattern 2: `~/.from-scratch` is the runtime clone

Distribution model: `git clone https://github.com/dimartinez/from-scratch.git ~/.from-scratch`. `from-scratch update` runs `git -C ~/.from-scratch pull --ff-only`. There is no pip, no venv, no PyPI release.

### Pattern 3: Preconditions are in install.sh, not in Python

Version checks (`python3 >= 3.8`), tool checks (`git`, `python3`), npm-legacy detection live in `install.sh` and exit with code `3` on missing requirements. Don't re-implement these checks inside Python — they have already passed by the time `cli.py` runs.

### Pattern 4: PATH hint is not a hard error

If `~/.local/bin` is not on `PATH`, install.sh **warns** and exits 0. The wrapper still got written — the user just has to put it on `PATH`. Preserve this UX (`exit 1` here would be hostile in a `curl | bash` context).

---

## Decision Tree

```
Renaming src/cli.py?              → Don't. Or update install.sh AND warn that all installs need re-running.
Adding a second entry-point?      → Add a second wrapper in install.sh, same PYTHONPATH export.
Adding a runtime dependency?      → Don't (see python-stdlib-only). The wrapper has no pip step.
Need to gate by Python version?   → Add the check to install.sh, fail with exit 3 + Spanish remediation.
```

---

## Code Examples

### Example 1: Imports must use `src.` prefix

```python
# WRONG — works locally with `PYTHONPATH=src`, breaks under the wrapper.
from catalog.manifest import parse_manifest

# RIGHT — works under both layouts.
from src.catalog.manifest import parse_manifest
```

### Example 2: Adding a precondition check to install.sh

```bash
if ! command -v jq &>/dev/null; then
  echo "ERROR: Necesito jq. Instalalo con: brew install jq" >&2
  exit 3
fi
```

Spanish copy, exit code `3`, remediation as a runnable command — same shape as the existing checks.

---

## Commands

```bash
# Reinstall the wrapper from a local checkout (skips clone)
FROM_SCRATCH_REPO_URL="$PWD" bash install.sh

# Inspect the generated wrapper
cat ~/.local/bin/from-scratch

# Run the wrapper tests
python -m pytest tests/test_wrapper_bash.py tests/test_install_sh.py tests/test_install_sh_messaging.py
```

---

## Resources

- **Source**: [install.sh](../../install.sh)
- **Tests**: [tests/test_wrapper_bash.py](../../tests/test_wrapper_bash.py), [tests/test_install_sh.py](../../tests/test_install_sh.py)
- **Related skills**: `python-stdlib-only` (no pip step in the wrapper), `desp-spanish-ux` (error copy in install.sh).
