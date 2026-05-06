import pytest


def parse_args(args):
    from src.cli import parse_args
    return parse_args(args)


def test_no_args_shows_help(capsys):
    from src.cli import parse_args
    result = parse_args([])
    assert result is None or (hasattr(result, "subcommand") and result.subcommand is None)


def test_init_subcommand():
    result = parse_args(["init"])
    assert result.subcommand == "init"


def test_update_subcommand():
    result = parse_args(["update"])
    assert result.subcommand == "update"


def test_force_flag_on_init():
    result = parse_args(["init", "--force"])
    assert result.force is True


def test_force_flag_default_false():
    result = parse_args(["init"])
    assert result.force is False


def test_invalid_subcommand_raises_or_returns_none():
    # Should not crash with unhandled exception
    try:
        result = parse_args(["invalid-command"])
        # Either returns something indicating failure or None
        assert result is None or hasattr(result, "subcommand")
    except SystemExit:
        pass  # argparse may call sys.exit on invalid


def test_help_flag_exits(capsys):
    with pytest.raises(SystemExit) as exc:
        parse_args(["--help"])
    assert exc.value.code == 0
