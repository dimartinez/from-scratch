import sys
from pathlib import Path
from src.ui.output import print_file_list, print_summary, confirm_prompt, CATEGORY_PREFIX


def show_preview(diff_result: dict, backups: list = None, out=None, stdin=None) -> bool:
    if out is None:
        out = sys.stdout
    if backups is None:
        backups = []

    # Header: count summary
    print_summary(diff_result, out=out)

    # Body: each file with prefix
    for category in ("added", "modified", "unchanged", "unowned_conflict", "user_modified", "removed"):
        for entry in diff_result.get(category, []):
            prefix = CATEGORY_PREFIX.get(category, "?")
            print(f"{prefix} {entry['path']}", file=out)

    # Show planned backups
    if backups:
        print("", file=out)
        print("Backups planificados:", file=out)
        for _src, backup_path in backups:
            print(f"  -> {backup_path}", file=out)

    print("", file=out)
    return confirm_prompt("¿Continuar? [s/N] ", stdin=stdin)


def render_uninstall_preview(files, dirs, state_dir, tool_dir, wrapper):
    """Return the formatted uninstall preview string including the confirmation prompt."""
    home = Path.home()

    def fmt(p):
        p = Path(p)
        try:
            return "~/" + str(p.relative_to(home))
        except ValueError:
            return str(p)

    lines = [
        "Los siguientes elementos serán eliminados permanentemente:",
        "",
        f"  Archivos del catálogo ({len(files)}):",
    ]
    for f in files:
        lines.append(f"    {fmt(f)}")

    if dirs:
        lines.append("")
        lines.append("  Directorios vacíos que se limpiarán:")
        for d in dirs:
            lines.append(f"    {fmt(d)}")

    lines += [
        "",
        "  Estado de from-scratch:",
        f"    {fmt(state_dir)}  (directorio completo)",
        "",
        "  Tool y wrapper:",
        f"    {fmt(tool_dir)}  (directorio completo)",
        f"    {fmt(wrapper)}",
        "",
        "¿Confirmar desinstalación? Esta acción no se puede deshacer. [s/N] ",
    ]

    return "\n".join(lines)
