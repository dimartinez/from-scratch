import io
import pytest


def test_print_file_list_goes_to_stdout(capsys):
    from src.ui.output import print_file_list
    entries = [{"category": "added", "path": "commands/foo.md"}]
    print_file_list(entries)
    captured = capsys.readouterr()
    assert "+ commands/foo.md" in captured.out
    assert captured.err == ""


def test_print_summary_goes_to_stdout(capsys):
    from src.ui.output import print_summary
    diff = {"added": [{"path": "a.md"}], "modified": [], "unchanged": [], "unowned_conflict": [], "user_modified": [], "removed": []}
    print_summary(diff)
    captured = capsys.readouterr()
    assert "+" in captured.out
    assert captured.err == ""


def test_warn_goes_to_stderr(capsys):
    from src.ui.output import warn
    warn("something is off")
    captured = capsys.readouterr()
    assert "WARN" in captured.err
    assert captured.out == ""


def test_spinner_stderr_not_stdout(capsys):
    from src.ui.output import Spinner
    import io as _io
    fake_stderr = _io.StringIO()
    fake_stderr.isatty = lambda: False
    with Spinner("Procesando...", stderr=fake_stderr):
        pass
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "Procesando..." in fake_stderr.getvalue()
