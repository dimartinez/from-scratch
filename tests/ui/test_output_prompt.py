import io
import pytest


def confirm(message="¿Continuar? [s/N] ", stdin_text=""):
    from src.ui.output import confirm_prompt
    stdin = io.StringIO(stdin_text)
    return confirm_prompt(message, stdin=stdin)


def test_default_n_on_enter():
    assert confirm(stdin_text="\n") is False


def test_s_is_affirmative():
    assert confirm(stdin_text="s\n") is True


def test_y_is_affirmative():
    assert confirm(stdin_text="y\n") is True


def test_uppercase_s_is_affirmative():
    assert confirm(stdin_text="S\n") is True


def test_other_input_is_negative():
    assert confirm(stdin_text="no\n") is False
    assert confirm(stdin_text="nope\n") is False
    assert confirm(stdin_text="x\n") is False


def test_eof_returns_false():
    assert confirm(stdin_text="") is False
