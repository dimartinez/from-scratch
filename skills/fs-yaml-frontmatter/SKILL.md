---
name: fs-yaml-frontmatter
description: >
  The from-scratch frontmatter parser is hand-written and rejects nesting and lists by design.
  Trigger: When writing or editing frontmatter in catalog/ files, or modifying src/catalog/yaml_frontmatter.py.
metadata:
  version: '1.0.0'
---

## When to Use

Use this skill when:

- Authoring or editing the `---`-delimited block of any file in `catalog/commands/` or `catalog/stacks/`.
- Modifying or extending `src/catalog/yaml_frontmatter.py`.
- A contributor reports that valid-looking YAML is being rejected.

---

## Critical Patterns

### Pattern 1: Flat key/value only

The parser supports exactly one shape:

```yaml
---
key: value
another: "with spaces or quotes"
---
```

It rejects, with `ValueError`:

- `parent:` followed by indented children → "nested keys are not supported".
- Lines starting with `- ` → "list values are not supported".
- Bare keys with no value followed by indented content → same as above.
- Missing closing `---` → "Malformed frontmatter".
- Lines without a colon → "Invalid frontmatter line".

### Pattern 2: Quotes are stripped, not parsed

`key: "value"` and `key: 'value'` produce `value`. Mixed quotes (`"value'`) are not stripped. There is no number or boolean coercion — every value is a string.

### Pattern 3: Comments are allowed only on lines starting with `#`

Trailing inline comments (`key: value  # comment`) are **not** stripped — they become part of the value.

### Pattern 4: Don't reach for PyYAML

This project is stdlib-only (see `python-stdlib-only`). Any extension to the parser stays in `src/catalog/yaml_frontmatter.py` and stays Python 3.8 compatible.

---

## Decision Tree

```
Need a list?     → Don't. Use multiple flat keys or move structure into the body.
Need nesting?    → Don't. Flatten with a separator (e.g. `meta_owner:` instead of `meta:\n  owner:`).
Need a number?   → Store as string; cast on read.
Need multi-line? → Put the prose in the body, not the frontmatter.
```

---

## Code Examples

### Example 1: Valid frontmatter

```markdown
---
name: python-cli
description: Plantilla mínima de CLI Python.
template_url: https://github.com/dimartinez/python-cli-template
---

Body goes here.
```

### Example 2: What the parser rejects (and the error)

```yaml
---
deps:
  - pytest      # ValueError: list values are not supported
owner:
  name: Diego   # ValueError: nested keys are not supported
---
```

### Example 3: Workaround for "I really need a list"

Prefer comma-separated values that the consumer splits explicitly:

```yaml
---
tags: cli, python, despegar
---
```

`tags = "cli, python, despegar"`. The consumer does `[t.strip() for t in fm["tags"].split(",")]`.

---

## Commands

```bash
# Quick parse check
python -c "from src.catalog.yaml_frontmatter import parse; \
  print(parse(open('catalog/stacks/python-cli.md').read()))"

# Run frontmatter tests
python -m pytest tests/catalog/test_yaml_frontmatter.py -v
```

---

## Resources

- **Source**: [src/catalog/yaml_frontmatter.py](../../src/catalog/yaml_frontmatter.py)
- **Related skills**: `fs-catalog` (which fields each kind expects), `python-stdlib-only` (why this is hand-written).
