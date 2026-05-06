import pytest


def test_network_error_has_code_and_message():
    from src.errors import NetworkError
    err = NetworkError("No se pudo conectar a GitHub")
    assert hasattr(err, "code")
    assert isinstance(err.code, str)
    assert len(err.code) > 0
    assert str(err)


def test_manifest_parse_error_has_code_and_message():
    from src.errors import ManifestParseError
    err = ManifestParseError("catalog.json inválido")
    assert hasattr(err, "code")
    assert isinstance(err.code, str)
    assert len(err.code) > 0


def test_catalog_file_not_found_error_has_code_and_message():
    from src.errors import CatalogFileNotFoundError
    err = CatalogFileNotFoundError("catalog/commands/foo.md")
    assert hasattr(err, "code")
    assert isinstance(err.code, str)
    assert len(err.code) > 0


def test_state_corrupt_error_has_code_and_message():
    from src.errors import StateCorruptError
    err = StateCorruptError("JSON truncado")
    assert hasattr(err, "code")
    assert isinstance(err.code, str)
    assert len(err.code) > 0


def test_git_fast_forward_error_has_code_and_message():
    from src.errors import GitFastForwardError
    err = GitFastForwardError()
    assert hasattr(err, "code")
    assert isinstance(err.code, str)
    assert len(err.code) > 0


def test_errors_are_exceptions():
    from src.errors import (
        NetworkError, ManifestParseError, CatalogFileNotFoundError,
        StateCorruptError, GitFastForwardError
    )
    for ErrClass in [NetworkError, ManifestParseError, CatalogFileNotFoundError,
                     StateCorruptError, GitFastForwardError]:
        assert issubclass(ErrClass, Exception)


def test_readable_messages():
    from src.errors import NetworkError, StateCorruptError
    net_err = NetworkError("fallo de red")
    assert "fallo de red" in str(net_err)
    state_err = StateCorruptError("JSON roto")
    assert "JSON roto" in str(state_err)
