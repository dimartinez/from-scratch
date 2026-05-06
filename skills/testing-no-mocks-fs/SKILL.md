---
name: testing-no-mocks-fs
description: >
  Tests use pytest's tmp_path for real filesystem; unittest.mock.patch is reserved for subprocess and entry-point boundaries. No conftest.py — each test_*.py defines its own helpers.
  Trigger: When writing or reviewing tests under tests/, especially anything filesystem-related.
metadata:
  version: '1.0.0'
---

## When to Use

Use this skill when:

- Writing a new `test_*.py`.
- Reviewing a PR that introduces `mock.patch` over `pathlib`, `os`, or `open`.
- Tempted to add a shared `conftest.py`.
- A test feels slow or flaky and the instinct is to mock the filesystem to "fix" it.

---

## Critical Patterns

### Pattern 1: `tmp_path` for filesystem, always

`tmp_path` is a `pathlib.Path` provided by pytest, isolated per test, cleaned up automatically.

```python
def test_copy_file_writes_atomically(tmp_path):
    dest = tmp_path / "out.md"
    copy_file("hello", dest)
    assert dest.read_text() == "hello"
```

Mocking `pathlib.Path.write_text` or `open` is forbidden — those mocks let real bugs through (encoding, permissions, atomic rename) that `tmp_path` would catch.

### Pattern 2: `unittest.mock.patch` only at the boundary

Acceptable patches:

- `subprocess.run` / `subprocess.check_output` (so tests don't actually shell out).
- The high-level entry-points `run_init`, `run_update` when testing the CLI dispatcher.
- `urllib.request.urlopen` when testing network-bound code (none today, but the rule applies).

Anything else — especially `open`, `Path`, `os.rename`, `json.loads` — is out of bounds.

### Pattern 3: No `conftest.py`

Each `test_*.py` file defines its own helpers. Common patterns appear duplicated as `make_catalog`, `make_git_repo`, `make_state`. The duplication is **the convention** — it keeps each test file readable in isolation, with no implicit fixtures.

A newcomer's instinct ("this would be nicer with a fixture") is wrong here. Reviewers will reject `conftest.py`.

### Pattern 4: Subprocess tests for `install.sh` and the wrapper

`tests/test_install_sh.py` and `tests/test_wrapper_bash.py` invoke the real bash scripts inside a `tmp_path` HOME, then assert on the resulting filesystem. This is the same principle: real I/O, isolated environment, no mocks.

### Pattern 5: Assertions on `FromScratchError` check `code` and `remediation`

When a test expects an error, assert both fields — not just the message. This is what makes `tests/test_errors_actionable.py` an invariant of the error contract.

```python
with pytest.raises(StateCorruptError) as exc:
    read_state(corrupt_path)
assert exc.value.code == "STATE_CORRUPT"
assert "from-scratch init" in exc.value.remediation
```

---

## Decision Tree

```
Filesystem operation?       → tmp_path. Always.
Subprocess call?            → mock.patch on subprocess.run.
Network call?               → mock.patch on urllib (not on the helper above it).
Need a helper?              → Define it locally in the test file. No conftest.
Same helper in 4 files?     → Still local. Duplication is intentional here.
```

---

## Code Examples

### Example 1: Local helper inside a test file

```python
# tests/state/test_read_state.py
def make_state(path: Path, files: list) -> Path:
    payload = {"version": 1, "files": files, "last_sync_completed_at": "..."}
    path.write_text(json.dumps(payload))
    return path

def test_read_state_returns_dict(tmp_path):
    path = make_state(tmp_path / "state.json", files=[])
    state = read_state(path)
    assert state["files"] == []
```

`make_state` is duplicated in `test_write_state.py` and `test_state_corrupt.py` — by design.

### Example 2: Patching at the right boundary

```python
# tests/sync/test_git.py
@mock.patch("subprocess.run")
def test_clone_repo_classifies_network_failure(mock_run):
    mock_run.side_effect = subprocess.CalledProcessError(128, [], stderr=b"could not resolve host")
    with pytest.raises(NetworkError):
        clone_repo("https://example.invalid", Path("/tmp/x"))
```

### Example 3: What NOT to do

```python
# WRONG — patches a low-level primitive used everywhere
@mock.patch("pathlib.Path.write_text")
def test_copy_file(mock_write):
    ...

# WRONG — adds a conftest.py
# tests/conftest.py
@pytest.fixture
def make_catalog(tmp_path):
    ...
```

---

## Commands

```bash
# Full suite
python -m pytest

# Single file with verbose output
python -m pytest tests/sync/test_diff.py -v

# Stop on first failure (useful while iterating)
python -m pytest -x

# Find any conftest.py that has snuck in
find tests -name conftest.py
```

---

## Resources

- **Tests**: [tests/](../../tests/)
- **Pyproject**: [pyproject.toml](../../pyproject.toml) — `[tool.pytest.ini_options]`
- **Related skills**: `fs-error-contract` (what to assert on errors), `fs-atomic-writes` (the behavior `tmp_path` actually exercises).
