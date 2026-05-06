import pytest


def test_network_error_remediation():
    from src.errors import NetworkError
    err = NetworkError()
    assert hasattr(err, "remediation")
    assert "from-scratch update" in err.remediation


def test_git_fast_forward_error_remediation():
    from src.errors import GitFastForwardError
    err = GitFastForwardError()
    assert hasattr(err, "remediation")
    assert "git status" in err.remediation
    assert "git reset --hard origin/main" in err.remediation


def test_manifest_parse_error_remediation():
    from src.errors import ManifestParseError
    err = ManifestParseError("bad json")
    assert hasattr(err, "remediation")
    # Should reference re-cloning
    assert "rm -rf ~/.from-scratch" in err.remediation


def test_state_corrupt_error_remediation():
    from src.errors import StateCorruptError
    err = StateCorruptError("truncated")
    assert hasattr(err, "remediation")
    assert "rm" in err.remediation
    assert "from-scratch init" in err.remediation


def test_catalog_file_not_found_remediation():
    from src.errors import CatalogFileNotFoundError
    err = CatalogFileNotFoundError("catalog/commands/foo.md")
    assert hasattr(err, "remediation")
    assert "from-scratch update" in err.remediation


def test_remediation_is_non_empty_string():
    from src.errors import (
        NetworkError, ManifestParseError, CatalogFileNotFoundError,
        StateCorruptError, GitFastForwardError
    )
    for ErrClass in [NetworkError, ManifestParseError, CatalogFileNotFoundError,
                     StateCorruptError, GitFastForwardError]:
        err = ErrClass()
        assert isinstance(err.remediation, str)
        assert len(err.remediation.strip()) > 0
