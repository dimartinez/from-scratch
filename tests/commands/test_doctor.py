import hashlib
import json
import os
import pathlib
import shutil as shutil_module
from pathlib import Path
import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ok(name="test", detail="fine", category="estado"):
    from src.commands.doctor import CheckResult
    return CheckResult(name=name, status="ok", detail=detail, category=category)


def _warn(name="test", detail="w", remediation="from-scratch update", category="estado"):
    from src.commands.doctor import CheckResult
    return CheckResult(name=name, status="warn", detail=detail, remediation=remediation, category=category)


def _error(name="test", detail="e", remediation="from-scratch init", category="estado"):
    from src.commands.doctor import CheckResult
    return CheckResult(name=name, status="error", detail=detail, remediation=remediation, category=category)


def _make_valid_state(tmp_path, installed_files=None):
    state_path = tmp_path / ".state.json"
    state = {
        "installed_files": installed_files or [],
        "last_sync_started_at": "2026-01-01T00:00:00",
        "last_sync_completed_at": "2026-01-01T00:00:01",
    }
    state_path.write_text(json.dumps(state))
    return state_path


# ---------------------------------------------------------------------------
# 1.1 check_binary
# ---------------------------------------------------------------------------

def test_check_binary_found_in_path(monkeypatch):
    monkeypatch.setattr(shutil_module, "which", lambda name: "/usr/local/bin/from-scratch")
    from src.commands.doctor import check_binary
    result = check_binary()
    assert result.status == "ok"
    assert "/usr/local/bin/from-scratch" in result.detail


def test_check_binary_not_found_in_path(monkeypatch):
    monkeypatch.setattr(shutil_module, "which", lambda name: None)
    from src.commands.doctor import check_binary
    result = check_binary()
    assert result.status == "warn"
    assert result.remediation


# ---------------------------------------------------------------------------
# 1.2 check_state_file
# ---------------------------------------------------------------------------

def test_check_state_file_valid(tmp_path):
    state_path = _make_valid_state(tmp_path)
    from src.commands.doctor import check_state_file
    result = check_state_file(state_path)
    assert result.status == "ok"


def test_check_state_file_not_found(tmp_path):
    state_path = tmp_path / ".state.json"
    from src.commands.doctor import check_state_file
    result = check_state_file(state_path)
    assert result.status == "error"
    assert result.remediation


def test_check_state_file_corrupt(tmp_path):
    state_path = tmp_path / ".state.json"
    state_path.write_text("not valid json {{")
    from src.commands.doctor import check_state_file
    result = check_state_file(state_path)
    assert result.status == "error"
    assert "from-scratch init --force" in result.remediation


def test_check_state_file_incomplete_sync(tmp_path):
    state_path = tmp_path / ".state.json"
    state = {
        "installed_files": [],
        "last_sync_started_at": "2026-01-01T00:00:02",
        "last_sync_completed_at": "2026-01-01T00:00:01",
    }
    state_path.write_text(json.dumps(state))
    from src.commands.doctor import check_state_file
    result = check_state_file(state_path)
    assert result.status == "warn"


# ---------------------------------------------------------------------------
# 1.3 check_files_integrity
# ---------------------------------------------------------------------------

def _sha256(content):
    return hashlib.sha256(content.encode()).hexdigest()


def test_check_files_integrity_all_ok(tmp_path):
    content = "hello world"
    (tmp_path / "commands").mkdir()
    (tmp_path / "commands" / "foo.md").write_text(content)
    installed_files = [{"path": "commands/foo.md", "hash": _sha256(content)}]
    from src.commands.doctor import check_files_integrity
    results = check_files_integrity(installed_files, tmp_path)
    assert len(results) == 1
    assert results[0].status == "ok"


def test_check_files_integrity_missing_file(tmp_path):
    installed_files = [{"path": "commands/missing.md", "hash": "abc"}]
    from src.commands.doctor import check_files_integrity
    results = check_files_integrity(installed_files, tmp_path)
    assert len(results) == 1
    assert results[0].status == "error"
    assert "from-scratch update" in results[0].remediation


def test_check_files_integrity_hash_mismatch(tmp_path):
    (tmp_path / "commands").mkdir()
    (tmp_path / "commands" / "foo.md").write_text("modified content")
    installed_files = [{"path": "commands/foo.md", "hash": "differenthash000"}]
    from src.commands.doctor import check_files_integrity
    results = check_files_integrity(installed_files, tmp_path)
    assert len(results) == 1
    assert results[0].status == "warn"


def test_check_files_integrity_empty(tmp_path):
    from src.commands.doctor import check_files_integrity
    results = check_files_integrity([], tmp_path)
    assert results == []


# ---------------------------------------------------------------------------
# 1.4 check_orphan_tmp
# ---------------------------------------------------------------------------

def test_check_orphan_tmp_no_orphans(tmp_path):
    from src.commands.doctor import check_orphan_tmp
    result = check_orphan_tmp(tmp_path)
    assert result.status == "ok"


def test_check_orphan_tmp_with_orphans(tmp_path):
    (tmp_path / "foo.tmp.1234").write_text("stale")
    from src.commands.doctor import check_orphan_tmp
    result = check_orphan_tmp(tmp_path)
    assert result.status == "error"
    assert "*.tmp.*" in result.remediation


# ---------------------------------------------------------------------------
# 1.5 check_bak_files
# ---------------------------------------------------------------------------

def test_check_bak_files_no_backups(tmp_path):
    from src.commands.doctor import check_bak_files
    result = check_bak_files(tmp_path)
    assert result.status == "ok"


def test_check_bak_files_with_many_backups(tmp_path):
    d = tmp_path / "commands"
    d.mkdir()
    for i in range(1, 7):
        (d / f"foo.bak.{i}").write_text("backup")
    from src.commands.doctor import check_bak_files
    result = check_bak_files(tmp_path)
    assert result.status == "warn"


def test_check_bak_files_few_backups_ok(tmp_path):
    d = tmp_path / "commands"
    d.mkdir()
    for i in range(1, 4):
        (d / f"foo.bak.{i}").write_text("backup")
    from src.commands.doctor import check_bak_files
    result = check_bak_files(tmp_path)
    assert result.status == "ok"


# ---------------------------------------------------------------------------
# 1.6 format_text_report
# ---------------------------------------------------------------------------

def test_format_text_report_contains_all_sections():
    from src.ui.doctor import format_text_report
    results = [
        _ok(name="binario", detail="found", category="estado"),
        _ok(name="foo.md", detail="ok", category="archivos"),
        _ok(name="tmp_huerfanos", detail="none", category="residuos"),
    ]
    output = format_text_report(results)
    assert "[ESTADO]" in output
    assert "[ARCHIVOS]" in output
    assert "[RESIDUOS]" in output
    assert "=== RESUMEN ===" in output


def test_format_text_report_line_format():
    from src.ui.doctor import format_text_report
    results = [_ok(name="binario", detail="/usr/local/bin/from-scratch", category="estado")]
    output = format_text_report(results)
    assert "binario: /usr/local/bin/from-scratch → OK" in output


def test_format_text_report_resumen_only_warnings():
    from src.ui.doctor import format_text_report
    results = [_warn(name="state_file", detail="sync incompleta", remediation="from-scratch update", category="estado")]
    output = format_text_report(results)
    assert "=== RESUMEN ===" in output
    assert "from-scratch update" in output


def test_format_text_report_resumen_with_errors():
    from src.ui.doctor import format_text_report
    results = [_error(name="state_file", detail="corrupto", remediation="from-scratch init --force", category="estado")]
    output = format_text_report(results)
    assert "=== RESUMEN ===" in output
    assert "from-scratch init" in output or "from-scratch update" in output


def test_format_text_report_resumen_all_ok():
    from src.ui.doctor import format_text_report
    results = [_ok(name="binario", detail="found", category="estado")]
    output = format_text_report(results)
    assert "=== RESUMEN ===" in output
    assert "OK" in output


# ---------------------------------------------------------------------------
# 1.7 format_json_report
# ---------------------------------------------------------------------------

def test_format_json_report_structure():
    from src.ui.doctor import format_json_report
    results = [
        _ok(name="binario", category="estado"),
        _warn(name="state_file", remediation="from-scratch update", category="estado"),
        _error(name="foo.md", remediation="from-scratch update", category="archivos"),
    ]
    report = format_json_report(results)
    assert report["schema_version"] == "1"
    assert isinstance(report["timestamp"], str) and report["timestamp"]
    assert report["status"] == "error"
    assert isinstance(report["checks"], list)
    assert len(report["checks"]) == 3
    assert report["summary"]["error_count"] == 1
    assert report["summary"]["warn_count"] == 1


def test_format_json_report_status_ok():
    from src.ui.doctor import format_json_report
    results = [_ok(), _ok(name="b")]
    report = format_json_report(results)
    assert report["status"] == "ok"


def test_format_json_report_status_warn():
    from src.ui.doctor import format_json_report
    results = [_ok(), _warn()]
    report = format_json_report(results)
    assert report["status"] == "warn"


# ---------------------------------------------------------------------------
# 1.8 format_markdown_report
# ---------------------------------------------------------------------------

def test_format_markdown_report_structure():
    from src.ui.doctor import format_markdown_report
    results = [
        _ok(name="binario", detail="found", category="estado"),
        _warn(name="commands/foo.md", detail="modified", remediation="from-scratch update", category="archivos"),
        _error(name="tmp_huerfanos", detail="3 found", remediation="rm ~/.claude/**/*.tmp.*", category="residuos"),
    ]
    output = format_markdown_report(results)
    assert output.startswith("# from-scratch doctor")
    assert "| --- |" in output
    assert "## Resumen" in output


def test_format_markdown_report_remediation_in_detail_column():
    from src.ui.doctor import format_markdown_report
    results = [
        _warn(name="state_file", detail="sync incompleta", remediation="from-scratch update", category="estado"),
    ]
    output = format_markdown_report(results)
    assert "from-scratch update" in output


def test_format_markdown_report_sections():
    from src.ui.doctor import format_markdown_report
    results = [
        _ok(category="estado"),
        _ok(category="archivos"),
        _ok(category="residuos"),
    ]
    output = format_markdown_report(results)
    assert "##" in output


# ---------------------------------------------------------------------------
# 1.9 exit codes via run_doctor
# ---------------------------------------------------------------------------

def _stub_checks(monkeypatch, all_ok_results=None, file_results=None):
    from src.commands.doctor import CheckResult
    ok = all_ok_results or CheckResult(name="stub", status="ok", detail="", category="estado")
    monkeypatch.setattr("src.commands.doctor.check_binary", lambda: ok)
    monkeypatch.setattr("src.commands.doctor.check_state_file", lambda p: ok)
    monkeypatch.setattr("src.commands.doctor.check_files_integrity",
                        lambda f, p: file_results if file_results is not None else [])
    monkeypatch.setattr("src.commands.doctor.check_orphan_tmp", lambda p: ok)
    monkeypatch.setattr("src.commands.doctor.check_bak_files", lambda p: ok)
    monkeypatch.setattr("src.commands.doctor.write_doctor_log", lambda e, p: None)


def _make_args(use_json=False, use_markdown=False):
    import argparse
    return argparse.Namespace(json=use_json, markdown=use_markdown)


def test_run_doctor_exit_code_all_ok(monkeypatch):
    _stub_checks(monkeypatch)
    from src.commands.doctor import run_doctor
    code = run_doctor(_make_args())
    assert code == 0


def test_run_doctor_exit_code_only_warnings(monkeypatch):
    from src.commands.doctor import CheckResult
    warn = CheckResult(name="stub", status="warn", detail="w", remediation="fix", category="estado")
    monkeypatch.setattr("src.commands.doctor.check_binary", lambda: warn)
    monkeypatch.setattr("src.commands.doctor.check_state_file", lambda p: warn)
    monkeypatch.setattr("src.commands.doctor.check_files_integrity", lambda f, p: [])
    monkeypatch.setattr("src.commands.doctor.check_orphan_tmp", lambda p: warn)
    monkeypatch.setattr("src.commands.doctor.check_bak_files", lambda p: warn)
    monkeypatch.setattr("src.commands.doctor.write_doctor_log", lambda e, p: None)
    from src.commands.doctor import run_doctor
    code = run_doctor(_make_args())
    assert code == 1


def test_run_doctor_exit_code_with_error(monkeypatch):
    from src.commands.doctor import CheckResult
    error = CheckResult(name="stub", status="error", detail="e", remediation="fix", category="estado")
    ok = CheckResult(name="stub2", status="ok", detail="", category="estado")
    monkeypatch.setattr("src.commands.doctor.check_binary", lambda: error)
    monkeypatch.setattr("src.commands.doctor.check_state_file", lambda p: ok)
    monkeypatch.setattr("src.commands.doctor.check_files_integrity", lambda f, p: [])
    monkeypatch.setattr("src.commands.doctor.check_orphan_tmp", lambda p: ok)
    monkeypatch.setattr("src.commands.doctor.check_bak_files", lambda p: ok)
    monkeypatch.setattr("src.commands.doctor.write_doctor_log", lambda e, p: None)
    from src.commands.doctor import run_doctor
    code = run_doctor(_make_args())
    assert code == 2


# ---------------------------------------------------------------------------
# 2.1 PermissionError handling
# ---------------------------------------------------------------------------

def test_check_state_file_permission_error(monkeypatch, tmp_path):
    def raise_perm(*args, **kwargs):
        raise PermissionError("denied")
    monkeypatch.setattr(pathlib.Path, "read_text", raise_perm)
    from src.commands.doctor import check_state_file
    result = check_state_file(tmp_path / ".state.json")
    assert result.status == "error"
    assert result.remediation


def test_check_files_integrity_permission_error(monkeypatch, tmp_path):
    (tmp_path / "commands").mkdir()
    (tmp_path / "commands" / "foo.md").write_bytes(b"content")

    def raise_perm(*args, **kwargs):
        raise PermissionError("denied")
    monkeypatch.setattr(pathlib.Path, "read_text", raise_perm)
    installed_files = [{"path": "commands/foo.md", "hash": "abc"}]
    from src.commands.doctor import check_files_integrity
    results = check_files_integrity(installed_files, tmp_path)
    assert any(r.status == "error" for r in results)
    assert any(r.remediation for r in results)


def test_check_orphan_tmp_permission_error(monkeypatch, tmp_path):
    def raise_perm(*args, **kwargs):
        raise PermissionError("denied")
    monkeypatch.setattr(pathlib.Path, "rglob", raise_perm)
    from src.commands.doctor import check_orphan_tmp
    result = check_orphan_tmp(tmp_path)
    assert result.status == "error"
    assert result.remediation


def test_check_bak_files_permission_error(monkeypatch, tmp_path):
    def raise_perm(*args, **kwargs):
        raise PermissionError("denied")
    monkeypatch.setattr(pathlib.Path, "rglob", raise_perm)
    from src.commands.doctor import check_bak_files
    result = check_bak_files(tmp_path)
    assert result.status == "error"
    assert result.remediation


# ---------------------------------------------------------------------------
# 3.1 RESUMEN block always present
# ---------------------------------------------------------------------------

def test_resumen_present_when_all_ok():
    from src.ui.doctor import format_text_report
    results = [_ok()]
    output = format_text_report(results)
    assert "=== RESUMEN ===" in output


def test_resumen_global_status_shown():
    from src.ui.doctor import format_text_report
    results = [_error()]
    output = format_text_report(results)
    lines = output.split("\n")
    resumen_idx = next(i for i, l in enumerate(lines) if "=== RESUMEN ===" in l)
    resumen_block = "\n".join(lines[resumen_idx:])
    assert "ERROR" in resumen_block or "error" in resumen_block.lower()


def test_resumen_hint_errors_present():
    from src.ui.doctor import format_text_report
    results = [_error(remediation="from-scratch init --force")]
    output = format_text_report(results)
    lines = output.split("\n")
    resumen_idx = next(i for i, l in enumerate(lines) if "=== RESUMEN ===" in l)
    resumen_block = "\n".join(lines[resumen_idx:])
    assert "from-scratch init" in resumen_block or "from-scratch update" in resumen_block


def test_resumen_hint_only_warnings():
    from src.ui.doctor import format_text_report
    results = [_warn()]
    output = format_text_report(results)
    lines = output.split("\n")
    resumen_idx = next(i for i, l in enumerate(lines) if "=== RESUMEN ===" in l)
    resumen_block = "\n".join(lines[resumen_idx:])
    assert "from-scratch update" in resumen_block


# ---------------------------------------------------------------------------
# 3.4 remediation null in JSON when ok
# ---------------------------------------------------------------------------

def test_format_json_report_remediation_null_when_ok():
    from src.ui.doctor import format_json_report
    results = [
        _ok(name="a"),
        _warn(name="b", remediation="from-scratch update"),
        _error(name="c", remediation="from-scratch init"),
    ]
    report = format_json_report(results)
    checks = {c["name"]: c for c in report["checks"]}
    assert checks["a"]["remediation"] is None
    assert checks["b"]["remediation"] == "from-scratch update"
    assert checks["c"]["remediation"] == "from-scratch init"


# ---------------------------------------------------------------------------
# 3.5 run_doctor output to stdout, nothing to stderr
# ---------------------------------------------------------------------------

def test_run_doctor_output_to_stdout_not_stderr(monkeypatch, capsys):
    from src.commands.doctor import CheckResult
    error = CheckResult(name="stub", status="error", detail="err", remediation="fix", category="estado")
    ok = CheckResult(name="stub2", status="ok", detail="", category="estado")
    monkeypatch.setattr("src.commands.doctor.check_binary", lambda: error)
    monkeypatch.setattr("src.commands.doctor.check_state_file", lambda p: ok)
    monkeypatch.setattr("src.commands.doctor.check_files_integrity", lambda f, p: [])
    monkeypatch.setattr("src.commands.doctor.check_orphan_tmp", lambda p: ok)
    monkeypatch.setattr("src.commands.doctor.check_bak_files", lambda p: ok)
    monkeypatch.setattr("src.commands.doctor.write_doctor_log", lambda e, p: None)

    from src.commands.doctor import run_doctor
    run_doctor(_make_args())

    out, err = capsys.readouterr()
    assert "[ESTADO]" in out or "estado" in out.lower()
    assert err == ""


# ---------------------------------------------------------------------------
# 4.1 write_doctor_log writes valid JSON line
# ---------------------------------------------------------------------------

def test_write_doctor_log_appends_valid_json(tmp_path):
    log_path = tmp_path / "doctor.log"
    entry = {"timestamp": "2026-01-01T00:00:00Z", "status": "ok", "error_count": 0, "warn_count": 0}
    from src.commands.doctor import write_doctor_log
    write_doctor_log(entry, log_path)
    lines = log_path.read_text().strip().splitlines()
    assert len(lines) == 1
    parsed = json.loads(lines[-1])
    assert parsed["timestamp"] == "2026-01-01T00:00:00Z"
    assert parsed["status"] == "ok"
    assert parsed["error_count"] == 0
    assert parsed["warn_count"] == 0


# ---------------------------------------------------------------------------
# 4.2 rotation keeps last 20 entries
# ---------------------------------------------------------------------------

def test_write_doctor_log_rotation(tmp_path):
    log_path = tmp_path / "doctor.log"
    existing = [json.dumps({"timestamp": f"2026-01-01T00:00:{i:02d}Z", "status": "ok",
                            "error_count": 0, "warn_count": 0}) for i in range(20)]
    log_path.write_text("\n".join(existing) + "\n")
    entry = {"timestamp": "2026-01-01T00:01:00Z", "status": "warn", "error_count": 0, "warn_count": 1}
    from src.commands.doctor import write_doctor_log
    write_doctor_log(entry, log_path)
    lines = [l for l in log_path.read_text().strip().splitlines() if l.strip()]
    assert len(lines) == 20
    last = json.loads(lines[-1])
    assert last["status"] == "warn"


# ---------------------------------------------------------------------------
# 4.3 best-effort: no exception on missing dir or permission error
# ---------------------------------------------------------------------------

def test_write_doctor_log_no_exception_on_missing_dir(tmp_path):
    log_path = tmp_path / "nonexistent" / "doctor.log"
    entry = {"timestamp": "2026-01-01", "status": "ok", "error_count": 0, "warn_count": 0}
    from src.commands.doctor import write_doctor_log
    write_doctor_log(entry, log_path)  # must not raise


def test_write_doctor_log_no_exception_on_rename_error(monkeypatch, tmp_path):
    def raise_perm(*args, **kwargs):
        raise PermissionError("denied")
    monkeypatch.setattr(os, "rename", raise_perm)
    log_path = tmp_path / "doctor.log"
    entry = {"timestamp": "2026-01-01", "status": "ok", "error_count": 0, "warn_count": 0}
    from src.commands.doctor import write_doctor_log
    write_doctor_log(entry, log_path)  # must not raise


# ---------------------------------------------------------------------------
# 5.1 CLI acceptance: doctor subcommand dispatching
# ---------------------------------------------------------------------------

def test_cli_doctor_dispatches_run_doctor(monkeypatch):
    captured = {}

    def fake_run_doctor(args):
        captured["args"] = args
        return 0

    monkeypatch.setattr("src.commands.doctor.run_doctor", fake_run_doctor)
    from src.cli import main
    code = main(["doctor"])
    assert code == 0
    assert captured.get("args") is not None


def test_cli_doctor_json_flag(monkeypatch):
    captured = {}

    def fake_run_doctor(args):
        captured["args"] = args
        return 0

    monkeypatch.setattr("src.commands.doctor.run_doctor", fake_run_doctor)
    from src.cli import main
    main(["doctor", "--json"])
    assert captured["args"].json is True


def test_cli_doctor_markdown_flag(monkeypatch):
    captured = {}

    def fake_run_doctor(args):
        captured["args"] = args
        return 0

    monkeypatch.setattr("src.commands.doctor.run_doctor", fake_run_doctor)
    from src.cli import main
    main(["doctor", "--markdown"])
    assert captured["args"].markdown is True


# ---------------------------------------------------------------------------
# 5.2 doctor subcommand help in Spanish
# ---------------------------------------------------------------------------

def test_cli_doctor_help_in_spanish(capsys):
    from src.cli import _build_parser
    parser = _build_parser()
    subparsers_action = next(
        a for a in parser._actions if hasattr(a, "_parser_class")
    )
    doctor_parser = subparsers_action.choices["doctor"]
    help_text = doctor_parser.format_help()
    spanish_keywords = ("instalación", "diagnóstico", "verificar", "estado", "from-scratch")
    assert any(kw in help_text for kw in spanish_keywords)


# ---------------------------------------------------------------------------
# 6.1 catalog.json includes doctor entry
# ---------------------------------------------------------------------------

def test_catalog_json_includes_doctor_entry():
    catalog_path = Path(__file__).parent.parent.parent / "catalog" / "catalog.json"
    data = json.loads(catalog_path.read_text())
    sources = [e["source"] for e in data["entries"]]
    assert "commands/from-scratch/doctor.md" in sources


# ---------------------------------------------------------------------------
# 6.2 doctor.md has parseable frontmatter with non-empty description
# ---------------------------------------------------------------------------

def test_doctor_md_has_valid_frontmatter():
    from src.catalog.yaml_frontmatter import parse
    doctor_md = Path(__file__).parent.parent.parent / "catalog" / "commands" / "from-scratch" / "doctor.md"
    text = doctor_md.read_text()
    metadata, _ = parse(text)
    assert metadata.get("description") and isinstance(metadata["description"], str)
