---
name: desp-spanish-ux
description: >
  All user-facing text (errors, hints, CLI descriptions, README, install.sh messages) is in Spanish; code identifiers and comments stay in English.
  Trigger: When writing strings the user will see — print/echo, argparse help, docstrings used as `--help`, error messages, README, hints.
metadata:
  version: '1.0.0'
---

## When to Use

Use this skill when:

- Editing `src/ui/hints.py`, `src/ui/errors.py`, `src/ui/output.py`, `src/ui/preview.py`.
- Adding `argparse` arguments or help text in `src/cli.py`.
- Writing or modifying messages in `install.sh`.
- Updating `README.md` or any user-facing markdown.
- Defining a new `FromScratchError` (the `message` and `remediation` are user-facing).

---

## Critical Patterns

### Pattern 1: Two languages, one rule each

| What                                     | Language |
| ---------------------------------------- | -------- |
| Module, class, function, variable names  | English  |
| Internal comments                        | English  |
| Error `code` (`STATE_CORRUPT`, etc.)     | English  |
| Error `message` (what the user reads)    | Spanish  |
| Error `remediation` (the fix command)    | Spanish (commands stay as-is, prose around them is Spanish) |
| `argparse` help / description / epilog   | Spanish  |
| `print_hint(...)` strings                | Spanish  |
| `install.sh` echo / WARN / ERROR         | Spanish  |
| README                                   | Spanish (with code blocks unchanged)            |

### Pattern 2: Despegar Spanish — informal `vos`, no English mixing

The existing copy uses Argentine Spanish: `corré`, `actualizá`, `tenés`, `agregalo`. Match it. Don't write `corre` (peninsular) or `correr` (infinitive). Don't slip into English ("Run `from-scratch update`") in the middle of a sentence — translate the verb (`Corré: from-scratch update`).

### Pattern 3: Centralize copy, don't sprinkle it

UI strings live in two places:

- **`src/ui/hints.py`** — non-error informational messages, keyed by name (`init_success`, `update_no_changes`, `incomplete_sync`, ...). Adding a hint adds a key.
- **`src/ui/errors.py`** + **`src/errors.py`** — error rendering. Each `FromScratchError` subclass owns its message and remediation.

When you need a new user-facing string, add it as a hint key or as part of an error class. Don't `print(...)` a Spanish string from inside `src/sync/` or `src/commands/` directly.

### Pattern 4: Commands inside copy stay English

```
"Corré: from-scratch update"   ✅
"Corré: actualizá from-scratch" ❌  (the binary is `from-scratch`, not Spanish)
```

The wrapping verb is Spanish; the executable, flags, and paths stay verbatim.

---

## Decision Tree

```
String the user will read?         → Spanish
Identifier or comment for devs?    → English
Error code / log code?             → English (SCREAMING_SNAKE_CASE)
README example?                    → Spanish prose, English code blocks
install.sh output?                 → Spanish (look at existing echos as the style guide)
Remediation containing a command?  → Spanish prose, command verbatim
```

---

## Code Examples

### Example 1: Adding a hint

```python
# src/ui/hints.py
if name == "update_remote_unreachable":
    return (
        "No pude conectar con el remoto. Reintentá cuando vuelva la red.\n"
        "Si querés trabajar offline: from-scratch init --skip-pull"
    )
```

### Example 2: Adding an error subclass

```python
class CatalogChecksumError(FromScratchError):
    code = "CATALOG_CHECKSUM_ERROR"
    remediation = (
        "Verificá que el clone esté íntegro: "
        "cd ~/.from-scratch && git status\n"
        "Si persiste, re-cloná: rm -rf ~/.from-scratch && curl -fsSL "
        "https://raw.githubusercontent.com/dimartinez/from-scratch/main/install.sh | bash"
    )

    def __init__(self, message: str = "El catálogo falló la verificación de integridad"):
        super().__init__(message)
```

### Example 3: argparse help in Spanish

```python
parser.add_argument(
    "--force",
    action="store_true",
    help="Pisa archivos modificados por el usuario y conflictos no-trackeados.",
)
```

---

## Commands

```bash
# Find user-facing strings that look English (heuristic — review by hand)
grep -nE 'print\("[A-Z][a-z]' src/ install.sh

# Quick translation reference: existing hints set the tone
grep -A1 'if name ==' src/ui/hints.py
```

---

## Resources

- **Source**: [src/ui/hints.py](../../src/ui/hints.py), [src/ui/errors.py](../../src/ui/errors.py), [src/errors.py](../../src/errors.py), [install.sh](../../install.sh)
- **Related skills**: `fs-error-contract` (where messages live), `fs-install-wrapper` (Spanish copy in install.sh).
