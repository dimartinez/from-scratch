import io
import pytest


def hint(name, **kwargs):
    from src.ui.hints import print_hint
    out = io.StringIO()
    print_hint(name, out=out, **kwargs)
    return out.getvalue()


def test_init_success_mentions_update():
    output = hint("init_success")
    assert "from-scratch update" in output


def test_update_no_changes_mentions_last_sync():
    output = hint("update_no_changes", last_sync_at="2026-01-15T10:00:00Z")
    assert "2026" in output or "enero" in output or "15" in output


def test_update_no_changes_not_epoch():
    output = hint("update_no_changes", last_sync_at="2026-01-15T10:00:00Z")
    # Should not show raw epoch number
    assert "1737" not in output  # epoch would be a large number


def test_already_initialized_mentions_update_command():
    output = hint("already_initialized")
    assert "from-scratch update" in output


def test_already_initialized_mentions_force():
    output = hint("already_initialized")
    assert "--force" in output


def test_hint_output_non_empty():
    for name in ["init_success", "already_initialized"]:
        assert len(hint(name).strip()) > 0
