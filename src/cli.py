#!/usr/bin/env python3
import argparse
import sys


SUBCOMMANDS = ["init", "update"]


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="from-scratch",
        description="Sincroniza el catálogo de Claude en ~/.claude/",
    )
    subparsers = parser.add_subparsers(dest="subcommand")

    init_parser = subparsers.add_parser(
        "init",
        help="Instala el catálogo por primera vez en ~/.claude/",
    )
    init_parser.add_argument(
        "--force",
        action="store_true",
        default=False,
        help="Sobreescribe archivos existentes (hace backup .bak.<timestamp>)",
    )

    update_parser = subparsers.add_parser(
        "update",
        help="Actualiza el catálogo en ~/.claude/ (hace git pull primero)",
    )
    update_parser.add_argument(
        "--force",
        action="store_true",
        default=False,
        help="Sobreescribe archivos modificados localmente",
    )

    return parser


def parse_args(args: list):
    parser = _build_parser()
    return parser.parse_args(args)


def _suggest_subcommand(given: str) -> str:
    best = None
    best_dist = float("inf")
    for cmd in SUBCOMMANDS:
        dist = _levenshtein(given, cmd)
        if dist < best_dist:
            best_dist = dist
            best = cmd
    return best if best_dist <= 3 else ""


def _levenshtein(a: str, b: str) -> int:
    m, n = len(a), len(b)
    dp = list(range(n + 1))
    for i in range(1, m + 1):
        prev = dp[0]
        dp[0] = i
        for j in range(1, n + 1):
            temp = dp[j]
            if a[i - 1] == b[j - 1]:
                dp[j] = prev
            else:
                dp[j] = 1 + min(prev, dp[j], dp[j - 1])
            prev = temp
    return dp[n]


def main(args=None):
    from src.errors import FromScratchError
    from src.ui.errors import render_error
    from src.ui.signal import handle_keyboard_interrupt, CANCEL_EXIT_CODE

    if args is None:
        args = sys.argv[1:]

    try:
        if not args:
            _build_parser().print_help()
            return 0

        parsed = parse_args(args)

        if parsed.subcommand is None:
            _build_parser().print_help()
            return 0

        if parsed.subcommand == "init":
            from src.commands.init import run_init
            return run_init(force=parsed.force)

        if parsed.subcommand == "update":
            from src.commands.update import run_update
            return run_update(force=parsed.force)

        suggestion = _suggest_subcommand(parsed.subcommand)
        msg = f"Subcomando desconocido: '{parsed.subcommand}'"
        if suggestion:
            msg += f". ¿Quisiste decir '{suggestion}'?"
        print(f"ERROR: {msg}", file=sys.stderr)
        return 1

    except KeyboardInterrupt:
        handle_keyboard_interrupt()
        return CANCEL_EXIT_CODE
    except FromScratchError as exc:
        return render_error(exc)
    except SystemExit:
        raise
    except Exception as exc:
        import traceback
        print(f"ERROR: {exc}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr, limit=5)
        return 1


if __name__ == "__main__":
    sys.exit(main())
