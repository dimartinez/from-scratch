import io
import sys
import pytest


def test_keyboard_interrupt_prints_cancelado(capsys):
    from src.ui.signal import handle_keyboard_interrupt
    fake_stderr = io.StringIO()
    handle_keyboard_interrupt(fake_stderr)
    assert "Cancelado" in fake_stderr.getvalue()


def test_keyboard_interrupt_message_to_stderr(capsys):
    from src.ui.signal import handle_keyboard_interrupt
    fake_stderr = io.StringIO()
    handle_keyboard_interrupt(fake_stderr)
    assert fake_stderr.getvalue() != ""


def test_no_traceback_in_output(capsys):
    from src.ui.signal import handle_keyboard_interrupt
    fake_stderr = io.StringIO()
    handle_keyboard_interrupt(fake_stderr)
    output = fake_stderr.getvalue()
    assert "Traceback" not in output
    assert "KeyboardInterrupt" not in output


def test_exit_code_is_2():
    from src.ui.signal import CANCEL_EXIT_CODE
    assert CANCEL_EXIT_CODE == 2
