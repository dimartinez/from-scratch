import io
import pytest


def print_file_list(entries, out=None):
    from src.ui.output import print_file_list
    return print_file_list(entries, out=out)


def test_added_prefix(capsys):
    out = io.StringIO()
    print_file_list([{"category": "added", "path": "commands/foo.md"}], out=out)
    assert out.getvalue().strip() == "+ commands/foo.md"


def test_modified_prefix(capsys):
    out = io.StringIO()
    print_file_list([{"category": "modified", "path": "commands/foo.md"}], out=out)
    assert out.getvalue().strip() == "~ commands/foo.md"


def test_unchanged_prefix():
    out = io.StringIO()
    print_file_list([{"category": "unchanged", "path": "commands/foo.md"}], out=out)
    assert out.getvalue().strip() == "= commands/foo.md"


def test_conflict_prefix():
    out = io.StringIO()
    print_file_list([{"category": "conflict", "path": "commands/foo.md"}], out=out)
    assert out.getvalue().strip() == "! commands/foo.md"


def test_one_line_per_file():
    out = io.StringIO()
    entries = [
        {"category": "added", "path": "commands/a.md"},
        {"category": "modified", "path": "commands/b.md"},
    ]
    print_file_list(entries, out=out)
    lines = out.getvalue().strip().splitlines()
    assert len(lines) == 2
