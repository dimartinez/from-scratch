import io
import pytest


def preview(diff_result, backups=None, out=None, stdin_text="s\n"):
    from src.ui.preview import show_preview
    if out is None:
        out = io.StringIO()
    stdin = io.StringIO(stdin_text)
    confirmed = show_preview(diff_result, backups=backups or [], out=out, stdin=stdin)
    return confirmed, out.getvalue()


def make_diff(**kwargs):
    base = {"added": [], "modified": [], "unchanged": [], "unowned_conflict": [], "user_modified": [], "removed": []}
    base.update(kwargs)
    return base


def test_header_shows_counts():
    diff = make_diff(added=[{"path": "a.md"}, {"path": "b.md"}], modified=[{"path": "c.md"}])
    confirmed, output = preview(diff)
    assert "+ 2" in output
    assert "~ 1" in output


def test_body_shows_paths_with_prefix():
    diff = make_diff(added=[{"path": "commands/foo.md"}])
    confirmed, output = preview(diff)
    assert "+ commands/foo.md" in output


def test_conflict_shown_with_exclamation():
    diff = make_diff(unowned_conflict=[{"path": "commands/mine.md"}])
    confirmed, output = preview(diff)
    assert "!" in output
    assert "commands/mine.md" in output


def test_backup_paths_shown():
    diff = make_diff(modified=[{"path": "commands/foo.md"}])
    backups = [("commands/foo.md", "commands/foo.md.bak.1234567890")]
    confirmed, output = preview(diff, backups=backups)
    assert ".bak." in output


def test_prompt_shown():
    diff = make_diff(added=[{"path": "a.md"}])
    confirmed, output = preview(diff)
    # Default 'n' if no input → not confirmed; but we passed 's'
    assert confirmed is True


def test_default_n_prompt():
    diff = make_diff(added=[{"path": "a.md"}])
    confirmed, _ = preview(diff, stdin_text="\n")
    assert confirmed is False
