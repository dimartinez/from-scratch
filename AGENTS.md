# from-scratch

> For AI agents: this file is your primary source of instructions.
> Module-level AGENTS.md files override this one when conflicts exist.

---

## Quick Start

```bash
# Install (no dependencies — stdlib only)
curl -fsSL https://raw.githubusercontent.com/dimartinez/from-scratch/main/install.sh | bash

# Run the CLI from a Python checkout
PYTHONPATH=src python -m cli --help

# Run tests
python -m pytest
```

---

## Project Overview

`from-scratch` is an internal Despegar CLI that bootstraps and syncs a curated catalog of Claude Code commands and stacks into the user's `~/.claude/` directory. It is distributed by `curl | bash` from a public GitHub mirror and runs on Python 3.8+ with zero runtime dependencies.

---

## Stack

| Module             | Location          | Technologies                                                     |
| ------------------ | ----------------- | ---------------------------------------------------------------- |
| CLI source         | `src/`            | Python `>=3.8`, stdlib only (argparse, json, hashlib, pathlib)   |
| Catalog payload    | `catalog/`        | `catalog.json` + Markdown files with plain YAML frontmatter      |
| Test suite         | `tests/`          | pytest (`test_*.py`, `tmp_path` for filesystem)                  |
| Installer          | `install.sh`      | Bash (`curl \| bash` entry-point, generates wrapper)             |
| Spec workflow      | `openspec/`       | OpenSpec spec-driven workflow (proposes / changes / specs)       |
| Build              | `pyproject.toml`  | setuptools legacy backend                                        |

---

## Structure

```
from-scratch/
├── src/                # CLI source — all imports must work with stdlib only
│   ├── cli.py          # argparse entry-point
│   ├── catalog/        # manifest + frontmatter + stack parsers
│   ├── commands/       # run_init, run_update orchestration
│   ├── state/          # .state.json read/write + SHA256 hashing
│   ├── sync/           # diff, copy (atomic), git wrappers
│   ├── ui/             # output, preview, errors, hints (Spanish copy)
│   └── errors.py       # FromScratchError hierarchy
├── catalog/            # Payload installed into ~/.claude/
│   ├── catalog.json    # Manifest of entries (kind = command | stack)
│   ├── commands/
│   └── stacks/
├── tests/              # pytest suite, mirrors src/ layout
├── openspec/           # Spec-driven change workflow
├── skills/             # AI agent skills (desp-skill-creator, project skills)
├── install.sh          # curl | bash installer + wrapper generator
└── pyproject.toml      # setuptools, pytest config, no runtime deps
```

---

## Architecture Boundaries

1. **`src/catalog/`** parses input (manifest + frontmatter) — never writes to disk.
2. **`src/sync/`** performs all filesystem mutations (`copy_file`, atomic writes, git operations) — only it touches `~/.claude/`.
3. **`src/state/`** owns `.state.json` — `compute_hash` (SHA256) tracks "what the CLI installed", not "what is on disk now". Drift detection depends on this distinction.
4. **`src/ui/`** is the only module that prints to stdout/stderr — commands and sync logic must not print directly.
5. **`src/commands/`** orchestrates the pipeline (`diff → preview → copy → write_state`); it must not embed parsing or I/O primitives.

---

## Critical Rules

**ALWAYS:**

- Read existing code before making changes.
- Propose changes before implementing (for non-trivial modifications).
- After code changes, assess whether AGENTS.md, related docs, or installed skills need updating — propose updates and wait for confirmation.
- Use the standard library only. Adding any runtime dependency (HTTP, YAML, hashing, etc.) is forbidden — implement with stdlib or copy the needed code inline.
- Keep Python 3.8 compatibility: no `match`/`case`, no `|` in type hints, no `tomllib`, no `dict | dict` merge.
- Write to `~/.claude/` and `.state.json` atomically: write to `*.tmp.{pid}` then `os.rename`, and clean up orphan `.tmp.*` files on entry.
- Every new exception must inherit from `FromScratchError` and define a `code` (`SCREAMING_SNAKE_CASE`) and a `remediation` (an executable command or actionable hint).
- Run any non-trivial change through the OpenSpec workflow: `propose → apply → archive`, with the three reviewers (`ux-reviewer`, `agentic-reviewer`, `tdd-reviewer`).
- Write user-facing copy (errors, hints, CLI descriptions, README) in **Spanish**; keep code identifiers and comments in English.

**NEVER:**

- Remove or weaken existing tests without explicit direction.
- Add a runtime dependency to `pyproject.toml`.
- Create a `conftest.py` — each `test_*.py` defines its own helpers (`make_catalog`, `make_git_repo`, etc.) by convention.
- Mock the filesystem in tests — use `tmp_path`. `unittest.mock.patch` is allowed only for subprocess and entry-point boundaries (`run_init`, `run_update`).
- Use a YAML feature beyond plain key/value: the parser in `src/catalog/yaml_frontmatter.py` is hand-written and rejects nesting and lists.
- Change the `src/` layout without updating `install.sh` — the wrapper exports `PYTHONPATH=$HOME/.from-scratch` and depends on the current path.

---

## Security

**NEVER:**

- Commit secrets, tokens, API keys, passwords, or credentials to the repository.
- Log sensitive data (PII, credit/debit card numbers, personal customer data, tokens, passwords, session IDs) at any log level.
- Disable security checks (skip SSL validation, disable CSRF).
- Use string concatenation to build SQL queries, shell commands, or URL parameters.
- Trust user input without validation — treat all external input as untrusted.
- Store passwords in plain text or use weak hashing algorithms.

**ALWAYS:**

- Use parameterized queries for all database access.
- Validate and sanitize inputs at system boundaries.
- Use environment variables or secret managers for credentials — never hardcode them.
- Scan for hardcoded credentials before every commit.
- Escape output to prevent XSS when rendering user-provided content.

**Project-specific:**

- Never run shell commands with `shell=True` and an interpolated string. The CLI invokes `git` via `subprocess` with an argv list — keep it that way.
- Treat the catalog payload as untrusted input: a malformed `catalog.json` or frontmatter must surface as a `FromScratchError`, never crash the process or silently overwrite user files.

---

## Safety Boundaries

**Ask the developer first before:**

- Deleting files, branches, or database tables.
- Running destructive commands (`rm -rf`, `DROP TABLE`, `git reset --hard`).
- Force-pushing (`git push --force`).
- Deploying to any environment.
- Adding new dependencies with broad impact.
- Modifying CI/CD pipelines or infrastructure configuration.

**After completing changes:**

- After adding new dependencies, ask the developer if they want to run a vulnerability scan on them.
- After adding or changing behavior, ask the developer if they want to analyze and increase test coverage of the affected files.

**NEVER:**

- Push directly to `main` or `master`.
- Edit generated files when a code generation workflow exists.
- Bypass pre-commit hooks or CI checks (`--no-verify`, `--skip-ci`).
- Run commands that expose credentials in terminal output or logs.

**Project-specific:**

- Never write outside `~/.claude/` or the project working tree. The CLI's blast radius is intentionally limited to those locations.
- Never overwrite a `user_modified` or `unowned_conflict` file without `--force` — the diff policy is the safety contract with the user.

---

## Conventions

- **Naming for skills:** global skills have no prefix (e.g. `python-3-8`); Despegar-internal use `desp-` (e.g. `desp-skill-creator`); app-specific use the app prefix `fs-` (e.g. `fs-catalog`).
- **Errors:** every `FromScratchError` subclass carries `code` + `remediation`; tests assert that `remediation` is an actionable command, not prose.
- **State file (`~/.claude/from-scratch/.state.json`):** SHA256 hashes represent "what the CLI installed", never "what is on disk now". Treat it as the source of truth for diffing, not for inspection.
- **Atomic writes:** every mutation under `~/.claude/` goes through `copy_file` (temp + rename) with optional `.bak.{ms_timestamp}` and orphan-tmp cleanup.
- **UI copy:** all user-facing strings live in `src/ui/hints.py` and `src/ui/errors.py` and are written in Spanish.
- **Diff categories:** `added`, `modified`, `unchanged`, `user_modified`, `unowned_conflict`, `removed`. The CLI never overwrites the last two without `--force`.

---

## Testing

```bash
# Full test suite
python -m pytest

# A single module
python -m pytest tests/sync/

# A single file
python -m pytest tests/test_cli_entrypoint.py -v
```

- Add tests for new behavior — cover success, failure, and edge cases.
- Use `tmp_path` (pytest fixture) for any filesystem work; never mock `pathlib`/`os`.
- Each `test_*.py` defines its own helpers locally (e.g. `make_catalog`, `make_git_repo`); do not introduce a shared `conftest.py`.
- `unittest.mock.patch` is allowed only at the boundary (`subprocess`, `run_init`, `run_update`).
- `FromScratchError` tests assert that `remediation` is an actionable shell command — preserve that contract when adding new error types.

---

## Git Workflow

- **Branch pattern:** `{feat|fix|chore|docs}/{short-description}` (e.g. `feat/python-curl-install`).
- **Commit style:** imperative, single-purpose; squash-merge via PR.
- **PR target:** `main`.
- **Pre-merge:** the OpenSpec change must pass through `propose → apply → archive`, reviewed by `ux-reviewer`, `agentic-reviewer`, and `tdd-reviewer`.

---

## Available Skills

| Action                                                    | Skill                  |
| --------------------------------------------------------- | ---------------------- |
| Create a new skill following the Despegar spec            | `desp-skill-creator`   |
| Edit `catalog/` entries — manifest, command, stack format | `fs-catalog`           |
| Reason about diff categories or `.state.json`             | `fs-state-sync`        |
| Author or edit YAML frontmatter (flat-only parser)        | `fs-yaml-frontmatter`  |
| Raise or render a `FromScratchError` correctly            | `fs-error-contract`    |
| Edit `install.sh` or anything that affects `~/.from-scratch` layout | `fs-install-wrapper` |
| Write to `~/.claude/` or `.state.json` safely             | `fs-atomic-writes`     |
| Choose a stdlib alternative instead of a runtime dep      | `python-stdlib-only`   |
| Avoid Python 3.10+ syntax; stay 3.8-compatible            | `python-3-8`           |
| Write tests with `tmp_path` (no filesystem mocks, no `conftest.py`) | `testing-no-mocks-fs` |
| Write user-facing copy in Despegar Spanish                | `desp-spanish-ux`      |
| Run a non-trivial change through `propose → apply → archive` | `openspec-workflow` |

---

## References

- [README.md](README.md) — User-facing installation and usage guide.
- [openspec/](openspec/) — Spec-driven change workflow (proposals, specs, changes).
- [.github/docs/agent_specifications.md](.github/docs/agent_specifications.md) — Source of truth for the project's required skills.
