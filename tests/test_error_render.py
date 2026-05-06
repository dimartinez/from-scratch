import io
import pytest


def render(err, stderr=None):
    from src.ui.errors import render_error
    return render_error(err, stderr=stderr)


def test_writes_to_stderr(capsys):
    from src.errors import NetworkError
    err = NetworkError("no connectivity")
    render(err)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "ERROR" in captured.err


def test_first_line_has_error_prefix(capsys):
    from src.errors import NetworkError
    err = NetworkError("no connectivity")
    render(err)
    captured = capsys.readouterr()
    lines = captured.err.strip().splitlines()
    assert lines[0].startswith("ERROR")


def test_second_line_has_remediation(capsys):
    from src.errors import NetworkError
    err = NetworkError("no connectivity")
    render(err)
    captured = capsys.readouterr()
    lines = captured.err.strip().splitlines()
    # remediation should appear somewhere after first line
    full_err = "\n".join(lines[1:])
    assert "from-scratch update" in full_err


def test_exit_code_runtime_error():
    from src.errors import NetworkError
    from src.ui.errors import render_error
    err = NetworkError()
    code = render_error(err)
    assert code == 1


def test_exit_code_state_corrupt():
    from src.errors import StateCorruptError
    from src.ui.errors import render_error
    err = StateCorruptError()
    code = render_error(err)
    assert code == 1


def test_exit_code_keyboard_interrupt():
    from src.ui.errors import exit_code_for
    assert exit_code_for(KeyboardInterrupt()) == 2


def test_exit_code_precondition(capsys):
    # GitFastForwardError is a precondition-style error -> exit code 1
    from src.errors import GitFastForwardError
    from src.ui.errors import render_error
    err = GitFastForwardError()
    code = render_error(err)
    assert code == 1
