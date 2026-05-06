import pytest
from unittest.mock import patch, MagicMock


def main(args):
    from src.cli import main
    return main(args)


def test_init_dispatches_to_run_init():
    with patch("src.commands.init.run_init", return_value=0) as mock_init:
        code = main(["init"])
    assert code == 0
    mock_init.assert_called_once()


def test_update_dispatches_to_run_update():
    with patch("src.commands.update.run_update", return_value=0) as mock_update:
        code = main(["update"])
    assert code == 0
    mock_update.assert_called_once()


def test_empty_args_shows_help_exits_0(capsys):
    code = main([])
    assert code == 0


def test_network_error_maps_to_exit_code_1(capsys):
    from src.errors import NetworkError
    with patch("src.commands.init.run_init", side_effect=NetworkError("no connection")):
        code = main(["init"])
    assert code == 1


def test_keyboard_interrupt_maps_to_exit_code_2(capsys):
    with patch("src.commands.init.run_init", side_effect=KeyboardInterrupt()):
        code = main(["init"])
    assert code == 2


def test_unexpected_exception_maps_to_exit_code_1(capsys):
    with patch("src.commands.init.run_init", side_effect=RuntimeError("unexpected")):
        code = main(["init"])
    assert code == 1


def test_help_flag_exits_0():
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
