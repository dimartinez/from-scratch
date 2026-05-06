import json
import pytest


def parse_manifest(path):
    from src.catalog.manifest import parse_manifest
    return parse_manifest(path)


def test_valid_entries_returned(tmp_path):
    catalog = {
        "entries": [
            {"kind": "command", "source": "commands/foo.md"},
            {"kind": "stack", "source": "stacks/bar.md"},
        ]
    }
    p = tmp_path / "catalog.json"
    p.write_text(json.dumps(catalog))
    entries = parse_manifest(p)
    assert len(entries) == 2
    assert entries[0]["kind"] == "command"
    assert entries[0]["source"] == "commands/foo.md"
    assert entries[1]["kind"] == "stack"


def test_recognized_kinds_command_and_stack(tmp_path):
    catalog = {
        "entries": [
            {"kind": "command", "source": "commands/a.md"},
            {"kind": "stack", "source": "stacks/b.md"},
        ]
    }
    p = tmp_path / "catalog.json"
    p.write_text(json.dumps(catalog))
    entries = parse_manifest(p)
    kinds = {e["kind"] for e in entries}
    assert "command" in kinds
    assert "stack" in kinds


def test_entry_without_source_raises(tmp_path):
    from src.errors import ManifestParseError
    catalog = {"entries": [{"kind": "command"}]}
    p = tmp_path / "catalog.json"
    p.write_text(json.dumps(catalog))
    with pytest.raises(ManifestParseError):
        parse_manifest(p)


def test_missing_catalog_json_raises(tmp_path):
    from src.errors import ManifestParseError
    with pytest.raises(ManifestParseError):
        parse_manifest(tmp_path / "catalog.json")


def test_invalid_json_raises(tmp_path):
    from src.errors import ManifestParseError
    p = tmp_path / "catalog.json"
    p.write_text("{bad json}")
    with pytest.raises(ManifestParseError):
        parse_manifest(p)


def test_requires_binary_field_ignored(tmp_path):
    catalog = {
        "requires_binary": "0.1.0",
        "entries": [
            {"kind": "command", "source": "commands/foo.md", "requires_binary": "1.0.0"},
        ],
    }
    p = tmp_path / "catalog.json"
    p.write_text(json.dumps(catalog))
    entries = parse_manifest(p)
    assert len(entries) == 1  # No exception raised


def test_requires_binary_absent_also_fine(tmp_path):
    catalog = {"entries": [{"kind": "command", "source": "commands/x.md"}]}
    p = tmp_path / "catalog.json"
    p.write_text(json.dumps(catalog))
    entries = parse_manifest(p)
    assert len(entries) == 1
