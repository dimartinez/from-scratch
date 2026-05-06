import os
import re
import time
from pathlib import Path

_TMP_PATTERN = re.compile(r"\.tmp\.\d+$")


def copy_file(content: str, dest: Path, backup: bool = False) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)

    if backup and dest.exists():
        timestamp = int(time.time() * 1000)
        backup_path = dest.with_suffix(f"{dest.suffix}.bak.{timestamp}")
        backup_path.write_text(dest.read_text(encoding="utf-8"), encoding="utf-8")

    _atomic_write(content, dest)


def _atomic_write(content: str, dest: Path) -> None:
    tmp = dest.parent / f"{dest.name}.tmp.{os.getpid()}"
    try:
        tmp.write_text(content, encoding="utf-8")
        os.rename(tmp, dest)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise


def cleanup_orphan_tmp_files(dest_base: Path) -> int:
    count = 0
    for f in dest_base.rglob("*"):
        if f.is_file() and _TMP_PATTERN.search(f.name):
            f.unlink(missing_ok=True)
            count += 1
    return count
