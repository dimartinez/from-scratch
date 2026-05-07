from datetime import datetime, timezone
from typing import List

_STATUS_TEXT = {
    "ok": "OK",
    "warn": "WARN",
    "error": "ERROR",
}

_STATUS_MD = {
    "ok": "✓ OK",
    "warn": "⚠ WARN",
    "error": "✗ ERROR",
}

_SECTION_HEADER_TEXT = {
    "estado": "[ESTADO]",
    "archivos": "[ARCHIVOS]",
    "residuos": "[RESIDUOS]",
}

_SECTION_HEADER_MD = {
    "estado": "## Estado del sistema",
    "archivos": "## Archivos instalados",
    "residuos": "## Residuos",
}

_SECTION_COL_MD = {
    "estado": "Check",
    "archivos": "Archivo",
    "residuos": "Tipo",
}

_CATEGORIES = ("estado", "archivos", "residuos")


def _global_status(results: list) -> str:
    if any(r.status == "error" for r in results):
        return "error"
    if any(r.status == "warn" for r in results):
        return "warn"
    return "ok"


def _resumen_text(results: list) -> List[str]:
    status = _global_status(results)
    lines = ["=== RESUMEN ==="]
    if status == "error":
        lines.append("estado: ERROR — hay errores en la instalación.")
        lines.append(
            "Tip: ejecutá `from-scratch init` o `from-scratch update` para reparar los errores listados arriba."
        )
    elif status == "warn":
        lines.append("estado: WARN — hay advertencias en la instalación.")
        lines.append("Tip: ejecutá `from-scratch update` para sincronizar la instalación.")
    else:
        lines.append("estado: OK — la instalación está en buen estado.")
        lines.append(
            "Consejo: ejecutá `from-scratch doctor` periódicamente o cuando algo no funcione como esperás."
        )
    return lines


def format_text_report(results: list) -> str:
    lines = []
    for category in _CATEGORIES:
        cat_results = [r for r in results if r.category == category]
        lines.append(_SECTION_HEADER_TEXT[category])
        for r in cat_results:
            status_label = _STATUS_TEXT.get(r.status, r.status.upper())
            line = f"{r.name}: {r.detail} → {status_label}"
            if r.status != "ok" and r.remediation:
                line += f" — {r.remediation}"
            lines.append(line)
        lines.append("")

    lines.extend(_resumen_text(results))
    return "\n".join(lines)


def format_json_report(results: list) -> dict:
    error_count = sum(1 for r in results if r.status == "error")
    warn_count = sum(1 for r in results if r.status == "warn")
    global_status = _global_status(results)

    checks = []
    for r in results:
        checks.append({
            "name": r.name,
            "category": r.category,
            "status": r.status,
            "detail": r.detail,
            "remediation": r.remediation if r.status != "ok" else None,
        })

    return {
        "schema_version": "1",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": global_status,
        "checks": checks,
        "summary": {
            "error_count": error_count,
            "warn_count": warn_count,
        },
    }


def format_markdown_report(results: list) -> str:
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    lines = [f"# from-scratch doctor ({timestamp})", ""]

    for category in _CATEGORIES:
        cat_results = [r for r in results if r.category == category]
        col = _SECTION_COL_MD[category]
        lines.append(_SECTION_HEADER_MD[category])
        lines.append(f"| {col} | Estado | Detalle |")
        lines.append("| --- | --- | --- |")
        for r in cat_results:
            status_md = _STATUS_MD.get(r.status, r.status.upper())
            detail = r.detail
            if r.status != "ok" and r.remediation:
                detail += f" — {r.remediation}"
            lines.append(f"| {r.name} | {status_md} | {detail} |")
        lines.append("")

    status = _global_status(results)
    lines.append("## Resumen")
    if status == "error":
        lines.append("**estado: ERROR** — hay errores en la instalación.")
        lines.append(
            "Tip: ejecutá `from-scratch init` o `from-scratch update` para reparar los errores listados arriba."
        )
    elif status == "warn":
        lines.append("**estado: WARN** — hay advertencias en la instalación.")
        lines.append("Tip: ejecutá `from-scratch update` para sincronizar la instalación.")
    else:
        lines.append("**estado: OK** — la instalación está en buen estado.")
        lines.append(
            "Consejo: ejecutá `from-scratch doctor` periódicamente o cuando algo no funcione como esperás."
        )

    return "\n".join(lines)
