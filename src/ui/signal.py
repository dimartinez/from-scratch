import sys

CANCEL_EXIT_CODE = 2


def handle_keyboard_interrupt(stderr=None) -> None:
    if stderr is None:
        stderr = sys.stderr
    print("\nCancelado por el usuario.", file=stderr)
