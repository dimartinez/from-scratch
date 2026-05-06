---
name: openspec-workflow
description: >
  Non-trivial changes go through OpenSpec: propose → apply → archive, reviewed by ux-reviewer, agentic-reviewer, and tdd-reviewer before merge.
  Trigger: When starting a non-trivial change, before writing code for a new feature, or when asked to implement something without an existing change folder.
metadata:
  version: '1.0.0'
---

## When to Use

Use this skill when:

- Starting any non-trivial change (new feature, behavior change, refactor that touches more than one module).
- Asked to "implement X" but no folder under `openspec/changes/` exists for it.
- Loading context before editing — check `openspec/changes/` for an active proposal.
- Wrapping up a change — the spec must be archived, not left open.

You can skip OpenSpec for trivial fixes (typos, single-line bug fixes, docstring tweaks) — but when in doubt, propose.

---

## Critical Patterns

### Pattern 1: Three phases, three slash commands

| Phase    | Command            | Output                                             |
| -------- | ------------------ | -------------------------------------------------- |
| Propose  | `/openspec-propose` | `openspec/changes/<change-name>/{proposal.md, design.md, tasks.md, specs/}` |
| Apply    | `/openspec-apply`   | Code + tests, ticking off `tasks.md`               |
| Archive  | `/openspec-archive` | Move the change folder under `openspec/changes/archive/` and update `openspec/specs/` |

The experimental variants `/opsx:propose`, `/opsx:apply`, `/opsx:archive` follow the same flow.

### Pattern 2: Three reviewers, run before merging

After `apply` and before `archive`, run the three review skills (each as an agent):

- `openspec-ux-reviewer` — CLI/user-facing UX of the spec.
- `openspec-agentic-reviewer` — fitness for agentic coding.
- `openspec-tdd-reviewer` — TDD quality (tests-first, coverage of error paths, real assertions).

The composed `from-scratch:openspec-improve` skill runs all three in sequence.

### Pattern 3: Tasks are TDD by default

Each item in `tasks.md` is structured "write the failing test → make it pass → refactor". Don't jump straight to implementation — the TDD reviewer will reject it. (See the project-wide TDD preference noted by the user.)

### Pattern 4: Specs in `openspec/specs/` are the source of truth

Once a change is archived, its delta lands in `openspec/specs/<area>.md`. Future changes propose **against the current spec**, not against the codebase intuition. Read the relevant spec before drafting a proposal.

### Pattern 5: One change at a time

Don't open three proposals in parallel for the same area — they will conflict on the spec deltas. Sequence them. The `/sync` skill assumes a single in-flight change at a time.

---

## Decision Tree

```
Trivial fix (typo, 1-line bug)?               → Skip OpenSpec, just patch + test.
New feature or behavior change?                → /openspec-propose first.
Refactor crossing module boundaries?           → Propose. The spec deltas are useful.
About to apply without a change folder?        → Stop. Propose first.
Apply done, code is green?                     → Run the three reviewers, then /openspec-archive.
Multiple proposals open in same area?          → Sequence them; merge one before opening the next.
```

---

## Code Examples

### Example 1: A typical change folder

```
openspec/changes/add-checksum-validation/
├── proposal.md       # WHY + scope + non-goals
├── design.md         # HOW (data flow, contracts, edge cases)
├── tasks.md          # TDD-ordered checklist
└── specs/
    └── catalog/
        └── delta.md  # What sections of openspec/specs/catalog.md change
```

### Example 2: Loading context before editing

Before writing code for "checksum validation", read in this order:

1. `openspec/specs/catalog.md` (current spec)
2. `openspec/changes/add-checksum-validation/proposal.md` (what is changing and why)
3. `openspec/changes/add-checksum-validation/design.md` (how)
4. `openspec/changes/add-checksum-validation/tasks.md` (next concrete step)

### Example 3: Tasks file (TDD shape)

```markdown
- [ ] Add `compute_checksum` failing test for empty catalog
- [ ] Implement `compute_checksum` to make the test pass
- [ ] Add failing test for `CatalogChecksumError` remediation
- [ ] Wire `CatalogChecksumError` into `parse_manifest`
- [ ] Run `python -m pytest` — green
- [ ] Run the three reviewers; address comments
- [ ] /openspec-archive
```

---

## Commands

```bash
# List active changes
ls openspec/changes/

# Read the current spec for an area
cat openspec/specs/<area>.md

# Run the full review cycle (composite skill in this repo)
# (invoke from chat, not bash): /from-scratch:openspec-improve
```

---

## Resources

- **Config**: [openspec/config.yaml](../../openspec/config.yaml)
- **Active changes**: [openspec/changes/](../../openspec/changes/)
- **Specs**: [openspec/specs/](../../openspec/specs/)
- **Reviewer skills**: `openspec-ux-reviewer`, `openspec-agentic-reviewer`, `openspec-tdd-reviewer`, `from-scratch:openspec-improve`.
- **Related skills**: `testing-no-mocks-fs` (TDD reviewer enforces the testing convention), `fs-error-contract` (UX reviewer flags missing remediations).
