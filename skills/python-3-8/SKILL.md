---
name: python-3-8
description: >
  Maintain Python 3.8 compatibility — no match/case, no `|` type unions, no `tomllib`, no `dict | dict` merge, no walrus tricks tied to newer typing.
  Trigger: When writing Python in src/, tests/, or any tool, especially when using newer syntax that linters might accept silently.
metadata:
  version: '1.0.0'
---

## When to Use

Use this skill when:

- Writing or reviewing any `.py` file in this project.
- Considering a "modern Python" idiom you saw in a 3.10+ tutorial.
- Editing `pyproject.toml`'s `requires-python`.
- A user reports a `SyntaxError` after upgrading or downgrading Python.

---

## Critical Patterns

### Pattern 1: Forbidden 3.10+ syntax

| Don't write                  | Use instead                                      | Rationale          |
| ---------------------------- | ------------------------------------------------ | ------------------ |
| `match x: case ...`          | `if/elif` chain or dict dispatch                 | 3.10+              |
| `int \| str` (in code)       | `Union[int, str]` from `typing`                  | 3.10+              |
| `list[int]` (in annotations) | `List[int]` from `typing`, or `from __future__ import annotations` at top | 3.9+ runtime |
| `a \| b` to merge dicts      | `{**a, **b}`                                     | 3.9+               |
| `import tomllib`             | Hand-parse, or use `json` for the data instead   | 3.11+              |
| `ExceptionGroup` / `except*` | Catch + iterate                                  | 3.11+              |
| `Self` from `typing`         | `"ClassName"` forward-reference string           | 3.11+              |

### Pattern 2: `from __future__ import annotations` is allowed but inconsistent

Some files in `src/` use it, some don't. If you add it, the entire module's annotations become strings (lazily evaluated) and you can use `list[int]` syntax safely. Don't sprinkle it on a single file just to use one new annotation — match the surrounding style.

### Pattern 3: Stdlib version gates

A few stdlib modules behave differently on 3.8:

- `Path.unlink(missing_ok=True)` — added in 3.8 ✅ (used today).
- `dict.__or__` (`|`) — 3.9+ ❌.
- `removeprefix` / `removesuffix` — 3.9+ ❌. Use slicing.
- `zoneinfo` — 3.9+ ❌. Use `datetime.timezone.utc` only (already the case).

### Pattern 4: CI-less environment makes local discipline matter

There is no `ruff` or `mypy` in CI. The 3.8 floor is enforced by `pyproject.toml`'s `requires-python` and by reviewers reading the code. A 3.10-only construct will pass on a developer's 3.12 machine and fail on a Mac with the system Python.

---

## Decision Tree

```
Is the syntax `int | str`, `match`, `dict | dict`, `tomllib`?    → Rewrite for 3.8.
Is it a stdlib method added after 3.8?                            → Use the 3.8 fallback.
Is it a typing-only annotation?                                   → Either `Union[...]` or `from __future__ import annotations`.
Are you tempted to bump `requires-python`?                        → Don't, without an OpenSpec proposal.
```

---

## Code Examples

### Example 1: Type unions

```python
# WRONG — 3.10+ syntax in code
def parse(x: int | str) -> int | None:
    ...

# RIGHT — works on 3.8
from typing import Optional, Union

def parse(x: Union[int, str]) -> Optional[int]:
    ...
```

### Example 2: Dict merge

```python
# WRONG — 3.9+
merged = base | overrides

# RIGHT — works on 3.8
merged = {**base, **overrides}
```

### Example 3: Pattern matching

```python
# WRONG — 3.10+
match kind:
    case "command": ...
    case "stack": ...

# RIGHT — explicit, works everywhere
if kind == "command":
    ...
elif kind == "stack":
    ...
else:
    raise ManifestParseError(...)
```

### Example 4: Verifying compatibility locally

```bash
# If you have pyenv:
pyenv shell 3.8.18 && python -m pytest

# Or Docker:
docker run --rm -v "$PWD":/app -w /app python:3.8-slim python -m pytest
```

---

## Commands

```bash
# Quick syntax check across src/ with the local interpreter
python -m compileall -q src/

# Find candidate violations textually
grep -rnE ': [A-Za-z_]+ \| [A-Za-z_]+' src/        # PEP 604 unions in code
grep -rn 'match ' src/                              # potential structural match
grep -rn 'tomllib' src/                             # 3.11+ stdlib
grep -rn 'removeprefix\|removesuffix' src/          # 3.9+ str methods
```

---

## Resources

- **Source**: [pyproject.toml](../../pyproject.toml) (`requires-python = ">=3.8"`)
- **Related skills**: `python-stdlib-only` (the version floor + zero-deps rule reinforce each other), `fs-install-wrapper` (the wrapper enforces `python3 >= 3.8` at install time).
