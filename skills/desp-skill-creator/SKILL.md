---
name: desp-skill-creator
description: >
    Creates new AI agent skills following Agent Skills specification.
    Trigger: When user wants to create a new skill, add agent instructions, or document AI patterns.
metadata:
    version: '1.0.0'
allowed-tools: Read, Edit, Write, Glob, Grep, Bash, WebFetch, WebSearch, Task
---

## When to Create a Skill

Create a skill when:

- A pattern is used repeatedly and AI needs guidance
- Project-specific conventions differ from generic best practices
- Complex workflows need step-by-step instructions
- Decision trees help AI choose the correct approach

**Don't create a skill when:**

- Documentation already exists (create a reference instead)
- Pattern is trivial or self-explanatory
- It's a one-time task

---

## Public vs Local Skills

### Public Skills (`skills/`)

**Create public skills for:**

- Team-wide patterns and conventions
- Standard project workflows
- Shared development practices
- Generic technology patterns (Angular, Java, etc.)

**Location:** `skills/{skill-name}/SKILL.md`

**Committed:** ✅ Yes (shared with all team members)

### Local Skills (`.github/local-skills/`)

**Create local skills for:**

- Personal workflow preferences
- Experimental patterns not ready for team adoption
- Company-specific integrations (internal tools, APIs)
- Personal deployment shortcuts
- Sensitive information that shouldn't be committed

**Location:** `.github/local-skills/{skill-name}/SKILL.md`

**Committed:** ❌ No (gitignored, user-only)

### Decision Tree

```
Is the skill a team standard? → Public skill (skills/)
Is the skill personal/experimental? → Local skill (.github/local-skills/)
Does the skill contain sensitive info? → Local skill (.github/local-skills/)
```

---

## Skill Structure

```
skills/{skill-name}/
├── SKILL.md              # Required - main skill file
├── assets/               # Optional - templates, schemas, examples
│   ├── template.ts
│   ├── template.java
│   └── schema.json
└── references/           # Optional - links to local docs
    └── docs.md           # Points to docs/*.md
```

**Project location**: All skills are in `./skills/` directory and accessed via:

- Direct: `./skills/{skill-name}/SKILL.md`
- Symlink (Windsurf): `.windsurf/skills/{skill-name}/SKILL.md`

---

## Critical Patterns

### SKILL.md Template Structure

Use template from [`assets/SKILL-TEMPLATE.md`](assets/SKILL-TEMPLATE.md) or create manually:

````markdown
---
name: { skill-name }
description: >
    {One-line description of what this skill does}.
    Trigger: {When AI should load this skill}.
metadata:
    version: '1.0'
---

## When to Use

{Bullet points of when to use this skill}

## Critical Patterns

{Most important rules - what AI MUST know}

## Code Examples

{Minimal and focused examples}

## Commands

```bash
{Common commands}
```

## Resources

- **Templates**: See [assets/](assets/) for {description}
- **Documentation**: See [references/](references/) for local docs
````

---

## Naming Conventions

Skill names follow a **scope-based prefix convention** to indicate their level of reusability:

| Scope                  | Prefix        | When to use                                                                     | Examples                                                     |
| ---------------------- | ------------- | ------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| **Global**             | _(none)_      | Technology or pattern reusable across any project, not tied to a company or app | `angular-15`, `typescript`, `java-21`, `spring-5`, `testing` |
| **Company (Despegar)** | `desp-`       | Shared across multiple Despegar apps but not reusable outside the company       | `desp-eva-ui`, `desp-skill-creator`                          |
| **App-specific**       | `{app-name}-` | Specific to a single application                                                | `s-activities-frontend`, `cars-domain`, `transfers-gui`      |

### Detailed patterns per type

| Type                     | Pattern                  | Examples                                                           |
| ------------------------ | ------------------------ | ------------------------------------------------------------------ |
| Generic skill            | `{technology}`           | `angular-15`, `typescript`, `rxjs`, `java-21`, `spring-5`, `maven` |
| Feature module           | `{app}-{feature}`        | `s-activities-frontend`, `cars-domain`, `transfers-gui`            |
| Testing skill            | `testing-{layer}`        | `testing`, `testing-backend`                                       |
| Tools (Despegar)         | `desp-{action}-{target}` | `desp-skill-creator`, `desp-flow-orchestrator`                     |
| Design system (Despegar) | `desp-{system-name}`     | `desp-eva-ui` (Despegar's EVA design system)                       |

---

## Decision: assets/ vs references/

```
Need code templates? → assets/
Need JSON schemas? → assets/
Need config examples? → assets/
Link to existing docs? → references/
Link to external guides? → references/ (with local path)
```

**Key Rule**: `references/` must point to LOCAL files (`docs/*.md`, `frontend/AGENTS.md`), not web URLs.

---

## Project Skill Categories

```
Generic (reusable) → angular-15, typescript, rxjs, java-21, spring-5, maven
Despegar shared → desp-eva-ui, desp-skill-creator
Project overview → {app-name}
Feature modules → {app-name}-{feature} (frontend, domain, gui, i18n, tracking)
Detail modules → {app-name}-detail-{type} (general, disney, universal, tour)
Search/Results → {app-name}-results, {app-name}-filters
Testing → {app-name}-testing, {app-name}-testing-backend
Workflows → Git/GitHub workflows (can exist as local skills)
Security/Deployment → {app-name}-security (deployment can exist as local skill)
Tools (Despegar) → desp-skill-creator, desp-{app-name}-orchestrator
```

### Project-Specific vs Generic Decision

```
Does pattern apply to ANY Angular/Java project? → Generic skill (e.g: angular-15, java-21, rxjs)
Is pattern specific to Company? → desp-{name} skill (e.g: desp-eva-ui)
Is pattern specific to an App? → {app-name}-{name} skill
Does generic skill need project context? → Add references/ pointing to project docs (frontend/AGENTS.md)
Company design system patterns? → desp-eva-ui skill
Cross-cutting workflow? → {project-name}-{workflow} (workflow, security, deployment)
```

**Examples:**

- `angular-15` (generic) vs `{project-name}-frontend` (project-specific architecture)
- `java-21` (generic) vs `{project-name}-domain` (project-specific service layer)
- `typescript` (generic) with `references/` pointing to `frontend/AGENTS.md` for project context

---

## Frontmatter Fields

| Field              | Required | Description                                       |
| ------------------ | -------- | ------------------------------------------------- |
| `name`             | Yes      | Skill identifier (lowercase, hyphens)             |
| `description`      | Yes      | What + Trigger in one block                       |
| `metadata.version` | No       | Semantic version as string                        |
| `model`            | No       | Model to use when this skill is active            |
| `context`          | No       | Set to 'fork' to run in a forked subagent context |
| `agent`            | No       | Subagent type to use when context: fork is set    |
| `hooks`            | No       | Hooks scoped to this skill's lifecycle            |

---

## Content Guidelines

### DO

- Start with most critical patterns
- Use tables for decision trees
- Keep code examples minimal and focused
- Include Commands section with copy-paste commands

### DON'T

- Add Keywords section (agent searches frontmatter, not body)
- Duplicate existing docs content (reference instead)
- Include long explanations (link to docs)
- Add troubleshooting sections (keep focused)
- Use web URLs in references (use local paths)

---

## Skill Registration

After creating the skill:

**1. Add to `CATALOG.md`:**

```markdown
| `{skill-name}` | {Description} | {Category} |
```

**2. Add to `AGENTS.md` (if used frequently):**

```markdown
| `{skill-name}` | {Description} | [SKILL.md](./skills/{skill-name}/SKILL.md) |
```

---

## Creation Checklist

- [ ] Skill doesn't already exist (check `skills/`)
- [ ] Pattern is reusable (not one-time)
- [ ] Name follows conventions (see Project Skill Categories above)
- [ ] Frontmatter is complete (description includes trigger keywords)
- [ ] Critical patterns are clear
- [ ] Code examples are minimal
- [ ] Commands section exists (if applicable)
- [ ] Added to `CATALOG.md`
- [ ] Added to `AGENTS.md` (if used frequently)

---

## Skill Management

### Skill Locations

- **Local project**: `./skills/{skill-name}/SKILL.md`
- **GitHub Copilot**: `.github/skills/{skill-name}/SKILL.md` (copy)
- **Cursor**: `.cursor/skills/{skill-name}/SKILL.md` (copy)
- **Windsurf (symlink)**: `.windsurf/skills/{skill-name}/SKILL.md` → `../skills/{skill-name}/SKILL.md`
- **Claude Global**: `.claude/skills/{skill-name}/SKILL.md` (copy)
- **OpenCode Global**: `~/.config/opencode/skill/{skill-name}/SKILL.md` (copy)
- **Gemini**: `.gemini/skills/{skill-name}/SKILL.md` (copy)
- **Codex**: `.codex/skills/{skill-name}/SKILL.md` (copy)
- **Antigravity**: `.antigravity/skills/{skill-name}/SKILL.md` (copy)

---

## Commands

```bash
# Create new skill directory
mkdir -p skills/{skill-name}

# Create skill file from template
cp skills/desp-skill-creator/assets/SKILL-TEMPLATE.md skills/{skill-name}/SKILL.md

# Create assets, scripts, and examples directories (optional)
mkdir -p skills/{skill-name}/assets
mkdir -p skills/{skill-name}/scripts
mkdir -p skills/{skill-name}/examples
mkdir -p skills/{skill-name}/references

# Validate skill structure
find skills/{skill-name} -type f -name "*.md"
```

---

## Resources

- **Templates**: See [assets/](assets/) for SKILL.md template
- **Documentation**: See [references/](references/) for local development guides
