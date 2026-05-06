import sys
from src.errors import FromScratchError


def render_error(err: Exception, stderr=None) -> int:
    """Print error to stderr and return the appropriate exit code."""
    if stderr is None:
        stderr = sys.stderr

    if isinstance(err, FromScratchError):
        print(f"ERROR: {err.message}", file=stderr)
        if err.remediation:
            print(err.remediation, file=stderr)
        return 1

    if isinstance(err, KeyboardInterrupt):
        print("Cancelado por el usuario.", file=stderr)
        return 2

    # Unexpected error
    print(f"ERROR: {err}", file=stderr)
    return 1


def exit_code_for(err: Exception) -> int:
    """Return exit code for a given exception without printing."""
    if isinstance(err, KeyboardInterrupt):
        return 2
    return 1
