---
name: fs-error-contract
description: >
  Every CLI exception inherits from FromScratchError and must define `code` (SCREAMING_SNAKE_CASE) and `remediation` (an executable command).
  Trigger: When raising, defining, or rendering exceptions anywhere in src/.
metadata:
  version: '1.0.0'
---

## When to Use

Use this skill when:

- Adding a new exception type or raising an existing one.
- Editing `src/errors.py` or `src/ui/errors.py` (`render_error`).
- A test under `tests/test_errors_actionable.py` is failing — the contract is being broken.

---

## Critical Patterns

### Pattern 1: One base class — `FromScratchError`

Defined in [src/errors.py](../../src/errors.py). Two class-level attributes are mandatory on every subclass:

- `code: str` — `SCREAMING_SNAKE_CASE`, stable identifier shown to the user (e.g. `STATE_CORRUPT`).
- `remediation: str` — at least one **executable** shell command the user can copy-paste. Prose alone fails the actionability test.

### Pattern 2: `remediation` is tested for actionability

`tests/test_errors_actionable.py` asserts that `remediation` contains a runnable command (typically `from-scratch ...`, `git ...`, or a `rm`/`curl` chain). If you add a new error, add a test case that proves the remediation runs.

### Pattern 3: Messages are in Spanish, codes are in English

The user-facing `message` and `remediation` are in Spanish (see `desp-spanish-ux`). The `code` and identifiers stay in English.

### Pattern 4: Never raise the base class directly

`FromScratchError` is abstract by convention. Always raise a subclass — `render_error` keys off the subclass behavior implicitly via the `code` field.

### Pattern 5: Wrap third-party errors at the boundary

When `subprocess`, `json`, or `pathlib` raise, catch and re-raise as a `FromScratchError` subclass with a useful `code`. Use `raise ... from exc` so the original traceback survives debugging.

---

## Decision Tree

```
Network/clone/pull failure?     → NetworkError
JSON or schema invalid?         → ManifestParseError
File referenced but missing?    → CatalogFileNotFoundError
.state.json unreadable/corrupt? → StateCorruptError
git pull cannot fast-forward?   → GitFastForwardError
None of the above?              → New subclass, with code + remediation, plus a test
```

---

## Code Examples

### Example 1: Defining a new error

```python
class CatalogChecksumError(FromScratchError):
    code = "CATALOG_CHECKSUM_ERROR"
    remediation = (
        "Re-cloná el catálogo: "
        "rm -rf ~/.from-scratch && curl -fsSL "
        "https://raw.githubusercontent.com/dimartinez/from-scratch/main/install.sh | bash"
    )

    def __init__(self, message: str = "El catálogo falló la verificación de integridad"):
        super().__init__(message)
```

### Example 2: Wrapping an stdlib error

```python
try:
    data = json.loads(content)
except json.JSONDecodeError as exc:
    raise ManifestParseError(f"catalog.json tiene JSON inválido: {exc}") from exc
```

### Example 3: What `render_error` shows the user

```
ERROR [STATE_CORRUPT] El state file está corrupto: Expecting value: line 1 column 1
Cómo seguir: rm ~/.claude/from-scratch/.state.json && from-scratch init
```

The `code`, the message, and the `remediation` all appear; reviewers will reject errors missing any.

---

## Commands

```bash
# Run all error-related tests
python -m pytest tests/test_errors.py tests/test_errors_actionable.py tests/test_error_render.py

# Quick smoke test of render_error
python -c "from src.errors import StateCorruptError; from src.ui.errors import render_error; \
  import sys; render_error(StateCorruptError('demo'), sys.stderr)"
```

---

## Resources

- **Source**: [src/errors.py](../../src/errors.py), [src/ui/errors.py](../../src/ui/errors.py)
- **Tests**: [tests/test_errors_actionable.py](../../tests/test_errors_actionable.py), [tests/test_error_render.py](../../tests/test_error_render.py)
- **Related skills**: `desp-spanish-ux` (message language), `fs-state-sync` (where `StateCorruptError` is raised).
