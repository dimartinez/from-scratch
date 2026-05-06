import sys
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
