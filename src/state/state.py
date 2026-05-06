import hashlib
import json
import os
from pathlib import Path
from typing import Optional


def default_state_path() -> Path:
    return Path.home() / ".claude" / "from-scratch" / ".state.json"


def read_state(path: Path) -> Optional[dict]:
    from src.errors import StateCorruptError
    try:
        content = path.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError):
        return None
    except UnicodeDecodeError as exc:
        raise StateCorruptError(f"El state file contiene bytes inválidos: {exc}") from exc

    try:
        data = json.loads(content)
    except (json.JSONDecodeError, ValueError) as exc:
        raise StateCorruptError(f"No se pudo parsear el state file: {exc}") from exc

    if not isinstance(data, dict):
        raise StateCorruptError(f"El state file tiene un formato inesperado (tipo: {type(data).__name__})")

    return data


def write_state(state: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(f".tmp.{os.getpid()}")
    try:
        tmp.write_text(json.dumps(state, indent=2), encoding="utf-8")
        os.rename(tmp, path)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise


def has_incomplete_sync(state: dict) -> bool:
    started = state.get("last_sync_started_at")
    if not started:
        return False
    completed = state.get("last_sync_completed_at")
    if not completed:
        return True
    return started > completed


def compute_hash(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()
