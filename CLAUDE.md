# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Read this first

The canonical instructions for this repo live in [AGENTS.md](AGENTS.md). Read it before proposing or making changes — it owns the architecture boundaries, critical rules (stdlib-only, Python 3.8 compatibility, atomic writes), the project skill catalog (`fs-*`, `desp-*`, `python-*`), and the OpenSpec workflow contract.

This file exists only because Claude Code auto-loads `CLAUDE.md` but not `AGENTS.md`. Treat any apparent conflict as `AGENTS.md` winning.

## Quick commands

```bash
# Run the CLI from a Python checkout
PYTHONPATH=src python -m cli --help

# Full test suite
python -m pytest

# A single test file
python -m pytest tests/test_cli_entrypoint.py -v
```
