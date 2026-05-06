import json
import pytest


def parse_manifest(path):
    from src.catalog.manifest import parse_manifest
    return parse_manifest(path)


def test_unknown_kind_does_not_raise(tmp_path):
    catalog = {"entries": [{"kind": "agent", "source": "agents/foo.md"}]}
    p = tmp_path / "catalog.json"
    p.write_text(json.dumps(catalog))
    entries = parse_manifest(p)
    assert isinstance(entries, list)


def test_unknown_kind_emits_warn_to_stderr(tmp_path, capsys):
    catalog = {"entries": [{"kind": "agent", "source": "agents/foo.md"}]}
    p = tmp_path / "catalog.json"
    p.write_text(json.dumps(catalog))
    parse_manifest(p)
    captured = capsys.readouterr()
    assert "WARN" in captured.err
    assert "agent" in captured.err
    assert "agents/foo.md" in captured.err


def test_unknown_kind_entry_omitted(tmp_path):
    catalog = {"entries": [{"kind": "agent", "source": "agents/foo.md"}]}
    p = tmp_path / "catalog.json"
    p.write_text(json.dumps(catalog))
    entries = parse_manifest(p)
    assert len(entries) == 0


def test_known_kinds_still_parsed_alongside_unknown(tmp_path):
    catalog = {
        "entries": [
            {"kind": "command", "source": "commands/a.md"},
            {"kind": "skill", "source": "skills/b.md"},
            {"kind": "stack", "source": "stacks/c.md"},
            {"kind": "comand", "source": "commands/typo.md"},  # typo
        ]
    }
    p = tmp_path / "catalog.json"
    p.write_text(json.dumps(catalog))
    entries = parse_manifest(p)
    assert len(entries) == 2
    kinds = {e["kind"] for e in entries}
    assert "command" in kinds
    assert "stack" in kinds


def test_multiple_unknown_kinds_each_get_warn(tmp_path, capsys):
    catalog = {
        "entries": [
            {"kind": "hook", "source": "hooks/a.md"},
            {"kind": "skill", "source": "skills/b.md"},
        ]
    }
    p = tmp_path / "catalog.json"
    p.write_text(json.dumps(catalog))
    parse_manifest(p)
    captured = capsys.readouterr()
    assert "hook" in captured.err
    assert "skill" in captured.err
