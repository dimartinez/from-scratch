import sys
import threading
import time

CATEGORY_PREFIX = {
    "added": "+",
    "modified": "~",
    "unchanged": "=",
    "conflict": "!",
    "user_modified": "!",
    "unowned_conflict": "!",
    "removed": "-",
}

SPINNER_CHARS = ["|", "/", "-", "\\"]


def warn(message: str, stderr=None) -> None:
    if stderr is None:
        stderr = sys.stderr
    print(f"WARN: {message}", file=stderr)


def print_file_list(entries: list, out=None) -> None:
    if out is None:
        out = sys.stdout
    for entry in entries:
        prefix = CATEGORY_PREFIX.get(entry.get("category", ""), "?")
        print(f"{prefix} {entry['path']}", file=out)


def print_summary(diff_result: dict, out=None) -> None:
    if out is None:
        out = sys.stdout
    order = [
        ("added", "+"),
        ("modified", "~"),
        ("unchanged", "="),
        ("unowned_conflict", "!"),
        ("user_modified", "!"),
        ("removed", "-"),
    ]
    for key, prefix in order:
        items = diff_result.get(key, [])
        if items:
            print(f"{prefix} {len(items)} {_label(key, len(items))}", file=out)


def _label(key: str, count: int) -> str:
    labels = {
        "added": "nuevo" if count == 1 else "nuevos",
        "modified": "modificado" if count == 1 else "modificados",
        "unchanged": "sin cambios",
        "unowned_conflict": "conflicto" if count == 1 else "conflictos",
        "user_modified": "modificado localmente" if count == 1 else "modificados localmente",
        "removed": "eliminado" if count == 1 else "eliminados",
    }
    return labels.get(key, key)


def confirm_prompt(message: str = "¿Continuar? [s/N] ", stdin=None) -> bool:
    if stdin is None:
        stdin = sys.stdin
    try:
        print(message, end="", flush=True, file=sys.stdout)
        answer = stdin.readline()
        if not answer:
            return False
        answer = answer.strip().lower()
        return answer in ("s", "y", "si", "yes")
    except EOFError:
        return False


class Spinner:
    def __init__(self, message: str = "Procesando...", stderr=None):
        self.message = message
        self._stderr = stderr or sys.stderr
        self._stop = threading.Event()
        self._thread = None
        self._is_tty = self._stderr.isatty()

    def __enter__(self):
        if self._is_tty:
            self._thread = threading.Thread(target=self._spin, daemon=True)
            self._thread.start()
        else:
            print(f"-> {self.message}", file=self._stderr)
        return self

    def __exit__(self, *args):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=1)
            print("\r" + " " * (len(self.message) + 5) + "\r", end="", file=self._stderr)

    def _spin(self):
        i = 0
        while not self._stop.is_set():
            char = SPINNER_CHARS[i % len(SPINNER_CHARS)]
            print(f"\r{char} {self.message}", end="", file=self._stderr, flush=True)
            time.sleep(0.1)
            i += 1
