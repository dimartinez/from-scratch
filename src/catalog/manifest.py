import json
import sys
from pathlib import Path

KNOWN_KINDS = {"command", "stack"}


def parse_manifest(path: Path) -> list:
    from src.errors import ManifestParseError

    try:
        content = path.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError) as exc:
        raise ManifestParseError(f"No se encontró catalog.json en {path}") from exc

    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ManifestParseError(f"catalog.json tiene JSON inválido: {exc}") from exc

    if not isinstance(data, dict):
        raise ManifestParseError("catalog.json no es un objeto JSON válido")

    raw_entries = data.get("entries", [])
    if not isinstance(raw_entries, list):
        raise ManifestParseError("El campo 'entries' de catalog.json debe ser una lista")

    entries = []
    for entry in raw_entries:
        kind = entry.get("kind", "")
        source = entry.get("source", "")

        if not source:
            raise ManifestParseError(
                f"Entrada en catalog.json sin campo 'source': {entry!r}"
            )

        if kind not in KNOWN_KINDS:
            print(
                f"WARN: Ignoré entrada con kind desconocido '{kind}' (source: {source}). "
                "Probablemente tu CLI está desactualizada; corré `from-scratch update`.",
                file=sys.stderr,
            )
            continue

        # Strip unknown fields, keep only what we need
        entries.append({"kind": kind, "source": source})

    return entries
