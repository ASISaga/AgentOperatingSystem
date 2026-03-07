# Skill Files Specification

**Version**: 1.0.0
**Status**: Active
**Last Updated**: 2026-03-07

## Overview

Specifies the format, structure, and conventions for GitHub Copilot agent skill files (`SKILL.md`) following the [agentskills.io](https://agentskills.io) specification. Skills live in `.github/skills/<skill-name>/`.

## Scope

- YAML frontmatter requirements for `SKILL.md` files
- Directory structure and subdirectory conventions
- Body structure and content guidelines
- Validation script patterns

## Specification

### File Format

Every `SKILL.md` must begin with valid YAML frontmatter:

```yaml
---
name: skill-name          # kebab-case; matches the directory name exactly
description: One-sentence purpose with discoverable keywords (1–1024 chars)
license: MIT
metadata:
  author: ASISaga
  version: "1.0"
  category: <category>    # see Categories below
  role: <role>            # see Roles below
allowed-tools: Bash(npm:*) Read Edit   # scoped tool access
---
```

### Required Fields

| Field | Type | Constraint |
|-------|------|-----------|
| `name` | string | kebab-case; must match the directory name |
| `description` | string | 1–1024 characters; keyword-rich for discoverability |
| `license` | string | License identifier (e.g., `MIT`) |
| `metadata.author` | string | Organisation or author name |
| `metadata.version` | string | Semantic version string (quoted) |
| `metadata.category` | string | One of the defined categories |
| `metadata.role` | string | One of the defined roles |
| `allowed-tools` | string | Space-separated tool access declarations |

### Directory Structure

```
.github/skills/skill-name/
├── SKILL.md              # Main skill definition (this file format)
├── scripts/              # Executable automation and validation scripts
│   └── validate-*.sh     # Exit 0 on success, non-zero on failure
├── references/           # Detailed specifications and reference content
│   └── *.md              # Static reference material (offloaded from SKILL.md)
└── assets/               # Visual examples (optional)
```

### Body Structure

`SKILL.md` files must follow this section order:

1. **Role and scope statement** — one-line summary
2. **Purpose paragraph** — what the skill does and why
3. **When to Use This Skill** — explicit activation triggers
4. **Core Principles or Responsibilities** — numbered list
5. **Workflows and Examples** — named step-by-step procedures with commands
6. **Tool Integration** — reference existing scripts and tools
7. **Validation Instructions** — how to verify the skill works
8. **Related Documentation** — cross-references to specs and docs

### Keep Concise

`SKILL.md` must be a lean entrypoint:

- Detailed specifications → `references/*.md`
- Long code examples → `references/examples.md`
- `SKILL.md` focuses on triggers, workflows, and tool integration

### Categories

| Category | Description |
|----------|-------------|
| `automation` | Scripts and workflow automation |
| `documentation` | Content creation and documentation management |
| `testing` | Quality assurance and validation |
| `meta-intelligence` | Agent self-improvement and evolution |
| `specification` | Specification-driven development workflows |

### Roles

| Role | Description |
|------|-------------|
| `lead-architect` | System-wide governance and design |
| `specialist` | Domain-specific expertise |
| `expert` | Deep technical knowledge in a narrow area |
| `specification-engineer` | SDD workflow and spec management |

### Validation Scripts

All scripts in `scripts/` must:

- Be executable (`chmod +x`)
- Return exit code `0` on success, non-zero on failure
- Print clear error messages
- Integrate with existing tools; never reimplement them

```bash
#!/bin/bash
set -e
FILE="$1"
if [ -z "$FILE" ]; then
  echo "Usage: $0 <file>"
  exit 1
fi
# Use existing tool
pylint "$FILE"
exit $?
```

## Validation

Before committing a skill:

1. YAML frontmatter is valid and parseable
2. All required fields are present
3. `name` matches the directory name in kebab-case
4. Scripts in `scripts/` are executable and return correct exit codes
5. `SKILL.md` body follows the required section order
6. Detailed content is offloaded to `references/`

```bash
# Validate YAML frontmatter
python -c "import yaml; yaml.safe_load(open('.github/skills/<name>/SKILL.md').read().split('---')[1])"

# Test validation scripts
./.github/skills/<name>/scripts/validate-*.sh
```

## References

→ **Framework**: `.github/docs/agent-intelligence-framework.md`
→ **Skill instructions**: `.github/instructions/skills.instructions.md`
→ **Agent spec**: `.github/specs/agents.md`
→ **Prompt spec**: `.github/specs/prompts.md`
→ **agentskills.io specification**: https://agentskills.io
→ **Repository spec**: `.github/specs/repository.md`
