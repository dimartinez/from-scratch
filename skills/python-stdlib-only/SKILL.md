---
name: python-stdlib-only
description: >
  Hard rule: from-scratch ships with zero runtime dependencies. Implement every feature with the standard library or copy the needed code inline.
  Trigger: When adding a feature that "would be easier with library X", editing pyproject.toml, or evaluating a third-party utility.
metadata:
  version: '1.0.0'
---

## When to Use

Use this skill when:

- Reaching for `requests`, `pyyaml`, `click`, `rich`, `pydantic`, or any third-party module.
- Editing `pyproject.toml`, especially the `[project]` section.
- Reviewing a PR that adds an import from a non-stdlib name.
- Designing a new feature that involves HTTP, YAML, hashing, atomic writes, retries, or pretty printing.

---

## Critical Patterns

### Pattern 1: `[project]` has no `dependencies`

Look at `pyproject.toml`: there is no `dependencies = [...]`. Adding one is a substantive design decision, not a maintenance edit. The CLI is distributed via `curl | bash` (see `fs-install-wrapper`); there is no `pip install` step.

### Pattern 2: Map every "I need X" to its stdlib equivalent

| Need                | Use                                                 |
| ------------------- | --------------------------------------------------- |
| HTTP                | `urllib.request` (GET/POST), `urllib.error` for retry classification |
| JSON                | `json`                                              |
| YAML (flat)         | `src/catalog/yaml_frontmatter.py` (hand-written)    |
| TOML                | `tomllib` only on 3.11+ — **forbidden** here (3.8). Parse by hand if needed. |
| Hashing             | `hashlib`                                           |
| Filesystem paths    | `pathlib`                                           |
| Atomic writes       | `tempfile` + `os.rename` (see `fs-atomic-writes`)   |
| CLI parsing         | `argparse`                                          |
| Subprocess          | `subprocess` with `argv` lists, never `shell=True`  |
| Concurrency         | `threading` or `concurrent.futures` (both stdlib)   |
| Retry / backoff     | Hand-rolled `for attempt in range(N): ... time.sleep(...)` |
| TTY detection       | `sys.stdout.isatty()`                               |
| Tabular output      | Manual `f"{a:<20} {b:>5}"` or `textwrap` — no `rich`/`tabulate` |

### Pattern 3: Copying inline beats adding a dep

If a third-party module has a small useful function (≤ 50 lines), reproduce it under `src/` with attribution in a comment. The licence-friendly cases are MIT/Apache/BSD; check before copying.

### Pattern 4: This rule applies at runtime — dev tools are different

`pytest` is OK as a dev tool (it lives outside the runtime). But you cannot import `pytest` from `src/`. The runtime/dev distinction is the only reason `pyproject.toml` references `pytest` config without listing it as a dependency.

---

## Decision Tree

```
Is the import in src/?                         → Must be stdlib. No exceptions.
Is the import only in tests/?                  → pytest + stdlib. Don't add new test deps without discussion.
Is the import in a build/CI script?            → Not part of the CLI; allowed (but there is no CI today).
Stdlib alternative exists but is uglier?       → Use it. Ergonomics is not a justification.
Stdlib alternative does not exist?             → Implement inline. If too large, propose via OpenSpec.
```

---

## Code Examples

### Example 1: HTTP without `requests`

```python
import json
import urllib.request
import urllib.error

def fetch_json(url: str, timeout: float = 5.0) -> dict:
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise NetworkError(f"No se pudo contactar {url}") from exc
```

### Example 2: Tabular output without `tabulate`

```python
def render_diff_table(rows):
    headers = ("Estado", "Archivo")
    widths = (max(len(r[0]) for r in [headers, *rows]), 0)
    yield f"{headers[0]:<{widths[0]}}  {headers[1]}"
    for state, path in rows:
        yield f"{state:<{widths[0]}}  {path}"
```

### Example 3: What NOT to do

```python
# WRONG — adds a runtime dep.
import yaml

# WRONG — adds a runtime dep.
from rich.console import Console

# WRONG — tomllib is 3.11+, project requires 3.8.
import tomllib
```

---

## Commands

```bash
# Verify no third-party imports leak into src/
python -m pytest                                      # The suite is the contract
grep -rE "^(import|from) " src/ | \
  grep -vE "^[^:]+:(import|from) (src|argparse|json|hashlib|pathlib|os|sys|re|time|datetime|subprocess|threading|urllib|typing|unittest|concurrent|tempfile|shutil|io)\\b"
# (any output from the grep above is a violation)
```

---

## Resources

- **Source**: [pyproject.toml](../../pyproject.toml), [src/](../../src/)
- **Related skills**: `python-3-8` (some stdlib modules are version-gated), `fs-install-wrapper` (why there is no pip step), `fs-yaml-frontmatter` (the hand-written YAML this rule forced).
