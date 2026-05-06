import io
import json
import pytest
from pathlib import Path


def make_catalog(catalog_dir: Path):
    catalog_dir.mkdir(parents=True, exist_ok=True)
    (catalog_dir / "catalog.json").write_text(json.dumps({"entries": [{"kind": "command", "source": "commands/foo.md"}]}))
    (catalog_dir / "commands").mkdir(exist_ok=True)
    (catalog_dir / "commands" / "foo.md").write_text("# Foo")
    return catalog_dir


def test_init_always_prints_preview_even_clean_dir(tmp_path):
    from src.commands.init import run_init
    catalog_dir = make_catalog(tmp_path / "catalog")
    dest_dir = tmp_path / "claude"
    state_file = tmp_path / ".state.json"

    out = io.StringIO()
    stdin = io.StringIO("s\n")
    run_init(catalog_dir=catalog_dir, dest_dir=dest_dir, state_path=state_file, out=out, stdin=stdin)

    output = out.getvalue()
    # Preview should show file list
    assert "commands/foo.md" in output


def test_init_preview_shows_counts(tmp_path):
    from src.commands.init import run_init
    catalog_dir = make_catalog(tmp_path / "catalog")
    dest_dir = tmp_path / "claude"
    state_file = tmp_path / ".state.json"

    out = io.StringIO()
    stdin = io.StringIO("s\n")
    run_init(catalog_dir=catalog_dir, dest_dir=dest_dir, state_path=state_file, out=out, stdin=stdin)

    output = out.getvalue()
    assert "+" in output  # Added count prefix
