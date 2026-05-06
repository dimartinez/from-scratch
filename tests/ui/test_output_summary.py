import io
import pytest


def print_summary(diff_result, out=None):
    from src.ui.output import print_summary
    return print_summary(diff_result, out=out)


def test_shows_added_count():
    out = io.StringIO()
    diff = {"added": [{"path": "a.md"}, {"path": "b.md"}], "modified": [], "unchanged": [], "unowned_conflict": [], "user_modified": [], "removed": []}
    print_summary(diff, out=out)
    assert "+ 2" in out.getvalue()


def test_shows_modified_count():
    out = io.StringIO()
    diff = {"added": [], "modified": [{"path": "a.md"}], "unchanged": [], "unowned_conflict": [], "user_modified": [], "removed": []}
    print_summary(diff, out=out)
    assert "~ 1" in out.getvalue()


def test_omits_zero_categories():
    out = io.StringIO()
    diff = {"added": [{"path": "a.md"}], "modified": [], "unchanged": [], "unowned_conflict": [], "user_modified": [], "removed": []}
    print_summary(diff, out=out)
    lines = out.getvalue().strip().splitlines()
    # Only one line (for added)
    assert len(lines) == 1


def test_stable_order():
    out = io.StringIO()
    diff = {
        "added": [{"path": "a.md"}],
        "modified": [{"path": "b.md"}],
        "unchanged": [{"path": "c.md"}],
        "unowned_conflict": [],
        "user_modified": [],
        "removed": [],
    }
    print_summary(diff, out=out)
    lines = out.getvalue().strip().splitlines()
    # added before modified before unchanged
    assert lines[0].startswith("+")
    assert lines[1].startswith("~")
    assert lines[2].startswith("=")


def test_all_zero_prints_nothing():
    out = io.StringIO()
    diff = {"added": [], "modified": [], "unchanged": [], "unowned_conflict": [], "user_modified": [], "removed": []}
    print_summary(diff, out=out)
    assert out.getvalue().strip() == ""
