---
name: <skill-name>
description: >
  <Brief description of what this skill enables>
  Trigger: <When AI should load this skill - be specific>
metadata:         # Optional
  version: "1.0.0"  # Optional
  compatibility: <Indicates environment requirements to function correctly>  # Optional
# allowed-tools: Read, Edit, Write, Glob, Grep, Bash  # Optional: Only if you need to restrict tools
model: <model-name>  # Optional: e.g. claude-3-5-sonnet-latest
context: fork        # Optional: set to fork for subagent
agent: <agent-type>  # Optional: e.g. browser
hooks: <action>      # Optional
---

<!--
- metadata.compatibility: (OPTIONAL) Indicates environment requirements to function correctly. 
  Use maximum 500 characters. Can specify intended product, system packages, network access, etc.
  Example: "Requires git, docker, jq, and internet access"

- allowed-tools: (OPTIONAL) Restrict which tools AI can use
  Include only if you need to limit tool access
  Available: Read, Edit, Write, Glob, Grep, Bash, WebFetch, WebSearch, Task
  Example: allowed-tools: Read, Grep  # Read-only skill
-->

## When to Use

Use this skill when:

- {Condition 1}
- {Condition 2}
- {Condition 3}

---

## Critical Patterns

{The MOST important rules - what AI MUST follow}

### Pattern 1: {Name}

```{language}
{code example}
```

### Pattern 2: {Name}

```{language}
{code example}
```

---

## Decision Tree

```
{Question 1}? → {Action A}
{Question 2}? → {Action B}
Otherwise     → {Default action}
```

---

## Code Examples

### Example 1: {Description}

```{language}
{minimal and focused example}
```

### Example 2: {Description}

```{language}
{minimal and focused example}
```

---

## Commands

```bash
{command 1}  # {description}
{command 2}  # {description}
{command 3}  # {description}
```

---
## Resources

- **Scripts**: See [scripts/](scripts/) for utility scripts.
- **Examples**: See [examples/](examples/) for real-world usage scenarios.
- **Templates**: See [assets/](assets/) for {template description}.
- **Documentation**: See [references/](references/) for links to local developer guides.
