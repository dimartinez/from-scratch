import sys
from datetime import datetime, timezone


def print_hint(name: str, out=None, **kwargs) -> None:
    if out is None:
        out = sys.stdout
    text = _get_hint(name, **kwargs)
    if text:
        print(text, file=out)


def _get_hint(name: str, **kwargs) -> str:
    if name == "init_success":
        return "Listo. Cuando quieras sincronizar con cambios del catálogo: from-scratch update"

    if name == "update_no_changes":
        last_sync_at = kwargs.get("last_sync_at", "")
        date_str = _format_date(last_sync_at) if last_sync_at else "desconocida"
        return f"Todo al día. (Última sincronización: {date_str})"

    if name == "already_initialized":
        return (
            "Ya está inicializado. Para sincronizar usá: from-scratch update\n"
            "Para reinstalar pisando todo: from-scratch init --force"
        )

    if name == "incomplete_sync":
        return "Detecté una instalación incompleta de la corrida previa."

    if name == "install_success":
        return "Listo. Probá `from-scratch init` para instalar el catálogo en ~/.claude/"

    if name == "already_uninstalled":
        return (
            "from-scratch no está instalado en este equipo.\n"
            "Para instalarlo: from-scratch init"
        )

    if name == "uninstall_success":
        return (
            "from-scratch desinstalado correctamente.\n"
            "Para volver a instalarlo: from-scratch init"
        )

    if name == "uninstall_cancelled":
        return "Desinstalación cancelada."

    return ""


def _format_date(iso_str: str) -> str:
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M UTC")
    except (ValueError, AttributeError):
        return iso_str
