import hashlib
import pytest


def sha256(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()


def test_write_state_with_hashes_and_read_back(tmp_path):
    from src.state.state import read_state, write_state
    content_a = "file content A"
    state = {
        "last_sync_started_at": "2026-01-01T00:00:00Z",
        "last_sync_completed_at": "2026-01-01T00:01:00Z",
        "installed_files": [
            {"path": "commands/foo.md", "hash": sha256(content_a)},
        ],
        "catalog_version": "abc",
    }
    path = tmp_path / ".state.json"
    write_state(state, path)
    result = read_state(path)
    assert result["installed_files"][0]["hash"] == sha256(content_a)


def test_different_content_different_hash():
    content_a = "content A"
    content_b = "content B"
    assert sha256(content_a) != sha256(content_b)


def test_same_content_same_hash():
    content = "same content"
    assert sha256(content) == sha256(content)


def test_state_hash_helper_produces_sha256():
    from src.state.state import compute_hash
    content = "hello world"
    result = compute_hash(content)
    expected = hashlib.sha256(content.encode()).hexdigest()
    assert result == expected


def test_compute_hash_deterministic():
    from src.state.state import compute_hash
    assert compute_hash("abc") == compute_hash("abc")
    assert compute_hash("abc") != compute_hash("xyz")
