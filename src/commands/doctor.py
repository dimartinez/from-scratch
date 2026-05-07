import json
import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class CheckResult:
    name: str
    status: str  # "ok", "warn", "error"
    detail: str = ""
    remediation: str = ""
    category: str = "estado"  # "estado", "archivos", "residuos"


def check_binary() -> CheckResult:
    path = shutil.which("from-scratch")
    if path:
        return CheckResult(name="binario", status="ok", detail=path, category="estado")
    return CheckResult(
        name="binario",
        status="warn",
        detail="No se encontró 'from-scratch' en PATH",
        remediation=(
            "curl -fsSL https://raw.githubusercontent.com/dimartinez/from-scratch/main/install.sh | bash"
        ),
        category="estado",
    )


def check_state_file(state_path: Path) -> CheckResult:
    from src.errors import StateCorruptError
    from src.state.state import read_state, has_incomplete_sync
    try:
        state = read_state(state_path)
    except StateCorruptError:
        return CheckResult(
            name="state_file",
            status="error",
            detail="El state file está corrupto",
            remediation="from-scratch init --force",
            category="estado",
        )

    if state is None:
        return CheckResult(
            name="state_file",
            status="error",
            detail="El state file no existe",
            remediation="from-scratch init",
            category="estado",
        )

    if has_incomplete_sync(state):
        return CheckResult(
            name="state_file",
            status="warn",
            detail="La última sincronización quedó incompleta",
            remediation="from-scratch update",
            category="estado",
        )

    last_sync = state.get("last_sync_completed_at", "—")
    installed_count = len(state.get("installed_files", []))
    detail = f"Última sync: {last_sync} · {installed_count} archivo(s)"
    return CheckResult(name="state_file", status="ok", detail=detail, category="estado")


def check_files_integrity(installed_files: list, base_path: Path) -> List[CheckResult]:
    from src.state.state import compute_hash
    results = []
    for entry in installed_files:
        file_path = base_path / entry["path"]
        try:
            content = file_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            results.append(CheckResult(
                name=entry["path"],
                status="error",
                detail=f"Archivo faltante en disco: {entry['path']}",
                remediation="from-scratch update",
                category="archivos",
            ))
            continue
        except PermissionError:
            results.append(CheckResult(
                name=entry["path"],
                status="error",
                detail=f"Sin permisos para leer: {entry['path']}",
                remediation=f"Verificá los permisos de {file_path}",
                category="archivos",
            ))
            continue

        actual_hash = compute_hash(content)
        if actual_hash == entry["hash"]:
            results.append(CheckResult(
                name=entry["path"],
                status="ok",
                detail=entry["path"],
                category="archivos",
            ))
        else:
            results.append(CheckResult(
                name=entry["path"],
                status="warn",
                detail=f"Hash diferente (modificado externamente): {entry['path']}",
                remediation="from-scratch update",
                category="archivos",
            ))
    return results


def check_orphan_tmp(base_path: Path) -> CheckResult:
    try:
        orphans = list(base_path.rglob("*.tmp.*"))
    except PermissionError:
        return CheckResult(
            name="tmp_huerfanos",
            status="error",
            detail="Sin permisos para buscar archivos .tmp.*",
            remediation="Verificá los permisos de ~/.claude/",
            category="residuos",
        )

    if not orphans:
        return CheckResult(
            name="tmp_huerfanos",
            status="ok",
            detail="Sin archivos .tmp.* huérfanos",
            category="residuos",
        )
    return CheckResult(
        name="tmp_huerfanos",
        status="error",
        detail=f"{len(orphans)} archivo(s) .tmp.* encontrado(s)",
        remediation="rm ~/.claude/**/*.tmp.*",
        category="residuos",
    )


def check_bak_files(base_path: Path) -> CheckResult:
    try:
        bak_files = list(base_path.rglob("*.bak.*"))
    except PermissionError:
        return CheckResult(
            name="bak_acumulados",
            status="error",
            detail="Sin permisos para buscar archivos .bak.*",
            remediation="Verificá los permisos de ~/.claude/",
            category="residuos",
        )

    if not bak_files:
        return CheckResult(
            name="bak_acumulados",
            status="ok",
            detail="Sin backups acumulados",
            category="residuos",
        )

    groups = {}
    for f in bak_files:
        base = f.name.split(".bak.")[0]
        groups.setdefault(base, []).append(f)

    max_count = max(len(v) for v in groups.values())
    if max_count >= 6:
        return CheckResult(
            name="bak_acumulados",
            status="warn",
            detail=f"{len(bak_files)} backup(s) acumulado(s)",
            remediation="rm ~/.claude/**/*.bak.*",
            category="residuos",
        )
    return CheckResult(
        name="bak_acumulados",
        status="ok",
        detail=f"{len(bak_files)} backup(s), dentro del límite",
        category="residuos",
    )


def write_doctor_log(entry: dict, log_path: Path) -> None:
    try:
        if log_path.exists():
            existing = [
                l for l in log_path.read_text(encoding="utf-8").splitlines() if l.strip()
            ]
        else:
            existing = []
        existing = existing[-19:]
        existing.append(json.dumps(entry))
        tmp = log_path.with_suffix(f".tmp.{os.getpid()}")
        tmp.write_text("\n".join(existing) + "\n", encoding="utf-8")
        os.rename(tmp, log_path)
    except Exception:
        pass


def run_doctor(args) -> int:
    from datetime import datetime, timezone
    from src.errors import StateCorruptError
    from src.state.state import default_state_path, read_state
    from src.ui.doctor import format_json_report, format_markdown_report, format_text_report

    state_path = default_state_path()
    base_path = state_path.parent.parent  # ~/.claude/

    binary_result = check_binary()
    state_result = check_state_file(state_path)

    installed_files = []
    try:
        state = read_state(state_path)
        if state:
            installed_files = state.get("installed_files", [])
    except (StateCorruptError, Exception):
        pass

    file_results = check_files_integrity(installed_files, base_path)
    orphan_result = check_orphan_tmp(base_path)
    bak_result = check_bak_files(base_path)

    all_results = [binary_result, state_result] + file_results + [orphan_result, bak_result]

    use_json = getattr(args, "json", False)
    use_markdown = getattr(args, "markdown", False)

    if use_json:
        import json as _json
        print(_json.dumps(format_json_report(all_results), indent=2))
    elif use_markdown:
        print(format_markdown_report(all_results))
    else:
        print(format_text_report(all_results))

    error_count = sum(1 for r in all_results if r.status == "error")
    warn_count = sum(1 for r in all_results if r.status == "warn")
    global_status = "error" if error_count > 0 else ("warn" if warn_count > 0 else "ok")

    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": global_status,
        "error_count": error_count,
        "warn_count": warn_count,
    }
    write_doctor_log(log_entry, state_path.parent / "doctor.log")

    if error_count > 0:
        return 2
    if warn_count > 0:
        return 1
    return 0
