import pytest


def test_truncated_json_raises_state_corrupt_error(tmp_path):
    from src.state.state import read_state
    from src.errors import StateCorruptError
    path = tmp_path / ".state.json"
    path.write_text('{"installed_files": [', encoding="utf-8")
    with pytest.raises(StateCorruptError):
        read_state(path)


def test_garbage_bytes_raises_state_corrupt_error(tmp_path):
    from src.state.state import read_state
    from src.errors import StateCorruptError
    path = tmp_path / ".state.json"
    path.write_bytes(b"\xff\xfe\x00\x01garbage")
    with pytest.raises(StateCorruptError):
        read_state(path)


def test_valid_json_wrong_shape_raises_state_corrupt_error(tmp_path):
    from src.state.state import read_state
    from src.errors import StateCorruptError
    path = tmp_path / ".state.json"
    # Valid JSON but not a dict (it's a list)
    path.write_text('[1, 2, 3]', encoding="utf-8")
    with pytest.raises(StateCorruptError):
        read_state(path)


def test_empty_file_raises_state_corrupt_error(tmp_path):
    from src.state.state import read_state
    from src.errors import StateCorruptError
    path = tmp_path / ".state.json"
    path.write_text('', encoding="utf-8")
    with pytest.raises(StateCorruptError):
        read_state(path)


def test_not_raw_json_decode_error(tmp_path):
    from src.state.state import read_state
    from src.errors import StateCorruptError
    path = tmp_path / ".state.json"
    path.write_text('{bad json}', encoding="utf-8")
    # Must raise StateCorruptError, not JSONDecodeError directly
    with pytest.raises(StateCorruptError):
        read_state(path)


def test_reader_does_not_leave_inconsistent_state(tmp_path):
    from src.state.state import read_state
    from src.errors import StateCorruptError
    path = tmp_path / ".state.json"
    path.write_text('{bad}', encoding="utf-8")
    try:
        read_state(path)
    except StateCorruptError:
        pass
    # A second call should raise again, not crash differently
    with pytest.raises(StateCorruptError):
        read_state(path)
