---
name: fs-catalog
description: >
  Contract for the from-scratch catalog format (catalog.json + flat YAML frontmatter).
  Trigger: When editing files under catalog/, parse_manifest, parse_stack, or anything that emits/consumes catalog entries.
metadata:
  version: '1.0.0'
---

## When to Use

Use this skill when:

- Adding, modifying, or removing entries in `catalog/catalog.json`.
- Writing or editing files under `catalog/commands/` or `catalog/stacks/`.
- Touching `src/catalog/manifest.py` or `src/catalog/stack.py`.
- A user reports that an entry is being silently ignored or rejected.

---

## Critical Patterns

### Pattern 1: `catalog.json` is `{ "entries": [...] }`

Each entry must have:

- `kind` — exactly `"command"` or `"stack"`. Unknown kinds are filtered with a `WARN:` to stderr.
- `source` — relative path under `catalog/`. Missing or empty `source` raises `ManifestParseError`.

Other fields are stripped silently. The parser keeps only `kind` and `source`.

### Pattern 2: `command` files require a `description` in frontmatter

Plain key/value YAML frontmatter, no nesting, no lists. Body is the prompt.

### Pattern 3: `stack` files require exactly three fields

`name`, `description`, `template_url` in the frontmatter. Anything missing raises `ValueError` from `parse_stack`. Extras in frontmatter are allowed but discarded.

### Pattern 4: Failure modes are not symmetric

- Bad JSON or missing `source` → `ManifestParseError` (process aborts via `render_error`).
- Unknown `kind` → printed warning, entry skipped, sync continues.
- Bad stack frontmatter → `ValueError` (caller is expected to wrap into `FromScratchError`).

When you add a new `kind`, update `KNOWN_KINDS` in `src/catalog/manifest.py`; otherwise existing installs print a warning until the user runs `from-scratch update`.

---

## Decision Tree

```
Adding a command?      → catalog/commands/<name>.md, frontmatter has `description:`
Adding a stack?        → catalog/stacks/<name>.md, frontmatter has name + description + template_url
New top-level kind?    → Update KNOWN_KINDS, add a parser, write tests, bump catalog
Entry must be hidden?  → Don't add it; "filter on read" is not supported
```

---

## Code Examples

### Example 1: Valid `catalog.json`

```json
{
  "entries": [
    { "kind": "command", "source": "commands/init.md" },
    { "kind": "stack", "source": "stacks/python-cli.md" }
  ]
}
```

### Example 2: Valid stack file

```markdown
---
name: python-cli
description: Plantilla de CLI Python con argparse y pytest.
template_url: https://github.com/dimartinez/python-cli-template
---

# Body — Markdown libre, ignorado por parse_stack.
```

### Example 3: What breaks silently

```json
{ "kind": "snippet", "source": "snippets/foo.md" }
```

`snippet` is not a known kind → entry is skipped with a stderr `WARN`. The user thinks they installed it; they did not.

---

## Commands

```bash
python -m pytest tests/catalog/                    # Validate parser changes
python -c "from src.catalog.manifest import parse_manifest; \
  from pathlib import Path; print(parse_manifest(Path('catalog/catalog.json')))"
```

---

## Resources

- **Source**: [src/catalog/manifest.py](../../src/catalog/manifest.py), [src/catalog/stack.py](../../src/catalog/stack.py)
- **Tests**: [tests/catalog/](../../tests/catalog/)
- **Related skill**: `fs-yaml-frontmatter` — the frontmatter parser is restrictive on purpose.
