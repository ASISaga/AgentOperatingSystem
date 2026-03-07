# Instruction Files Specification

**Version**: 1.0.0
**Status**: Active
**Last Updated**: 2026-03-07

## Overview

Specifies the format, structure, and conventions for GitHub Copilot path-specific instruction files (`*.instructions.md`) stored in `.github/instructions/`. Instruction files auto-load when Copilot edits files matching their `applyTo` glob pattern.

## Scope

- YAML frontmatter requirements for `*.instructions.md` files
- Naming conventions and `applyTo` glob patterns
- Content guidelines: what belongs here vs. in specs or docs
- Validation criteria

## Specification

### File Format

Every instruction file must begin with valid YAML frontmatter:

```yaml
---
applyTo: "glob/pattern/**"     # specific glob targeting exact file types
description: "Brief description for agent discovery (1–256 chars)"
---
```

### Required Fields

| Field | Type | Constraint |
|-------|------|-----------|
| `applyTo` | string | Specific glob pattern; avoid overly broad matches |
| `description` | string | 1–256 characters; enables agent discovery |

### Naming Conventions

- **File**: `<category>.instructions.md` (lowercase, kebab-case)
- Descriptive: `python.instructions.md`, not `py.instructions.md`
- Scoped: `azure-functions.instructions.md` for framework-specific guidance
- Meta: `github-specs.instructions.md` for `.github/` system files

### applyTo Patterns

Patterns must be specific and non-overlapping:

| File type | Pattern example |
|-----------|----------------|
| Python source | `**/*.py` |
| Agent files | `.github/agents/*.agent.md` |
| Prompt files | `.github/prompts/*.prompt.md` |
| Skill files | `.github/skills/*/SKILL.md` |
| Spec files | `.github/specs/*.md` |
| Instruction files | `.github/instructions/*.md` |
| Markdown docs | `docs/**/*.md,*.md` |

### Body Structure

Instruction files must follow this section order:

1. **Purpose** — what these files are and when the instruction applies
2. **File Format** — YAML frontmatter requirements and field descriptions
3. **Content Guidelines** — DO / DON'T lists for what belongs in this file type
4. **Tool Integration** — commands agents should run (tests, linters, scripts)
5. **Validation** — pre-commit checklist
6. **Related Documentation** — spec and doc cross-references

### Content Guidelines

✅ **DO Include:**
- File format requirements specific to the file type
- Coding standards and conventions for the matched file type
- Tool integration commands (test runners, linters, validation scripts)
- References to detailed specs and guides

❌ **DON'T Include:**
- Detailed specifications (belong in `.github/specs/`)
- Implementation guides and tutorials (belong in `.github/docs/`)
- Content already in `copilot-instructions.md` (no duplication)
- Overlapping `applyTo` patterns with other instruction files

### Lean Principle

Instruction files are the shortest path to the right spec. Keep them lean:

- Reference `.github/specs/<category>.md` for detailed patterns
- Reference `.github/docs/` for implementation guides
- Content in the instruction file should be a concise, scannable summary only

## Validation

Before committing an instruction file:

1. YAML frontmatter is valid and parseable
2. `applyTo` pattern is specific and does not overlap with other instruction files
3. Content references specs/docs rather than duplicating them
4. No content duplicated from `copilot-instructions.md`
5. Follows `<category>.instructions.md` naming convention

```bash
# Validate YAML frontmatter
python -c "import yaml; yaml.safe_load(open('.github/instructions/<name>.instructions.md').read().split('---')[1])"
```

## References

→ **Framework**: `.github/docs/agent-intelligence-framework.md`
→ **Instruction file standards**: `.github/instructions/github-instructions.instructions.md`
→ **Path-specific mechanism**: `.github/docs/path-specific-instructions.md`
→ **Agent spec**: `.github/specs/agents.md`
→ **Prompt spec**: `.github/specs/prompts.md`
→ **Skill spec**: `.github/specs/skills.md`
→ **Repository spec**: `.github/specs/repository.md`
