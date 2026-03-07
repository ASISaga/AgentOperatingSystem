# Agent Files Specification

**Version**: 1.0.0
**Status**: Active
**Last Updated**: 2026-03-07

## Overview

Specifies the format, structure, and conventions for GitHub Copilot Custom Agent files (`*.agent.md`) stored in `.github/agents/`.

## Scope

- YAML frontmatter requirements for `.agent.md` files
- Required fields and naming conventions
- Relationship between agent, prompt, and skill files
- Access and visibility rules

## Specification

### File Format

Every agent file must begin with valid YAML frontmatter:

```yaml
---
name: agent-name          # kebab-case; matches the file stem
description: "One-line description of agent purpose (1–256 chars)"
prompt: |
  Multi-line agent instructions that define the agent's role,
  responsibilities, activation triggers, and workflows.
tools: ['*']              # or an explicit list of allowed tools
---
```

### Required Fields

| Field | Type | Constraint |
|-------|------|-----------|
| `name` | string | kebab-case; must match the file stem |
| `description` | string | 1–256 characters; clear and discoverable |
| `prompt` | multiline string | Role, responsibilities, triggers, workflows |
| `tools` | list | `['*']` for all tools, or scoped list |

### Naming Conventions

- **File**: `<agent-name>.agent.md` (kebab-case)
- **`name` field**: matches file stem exactly (`agent-name`)
- **`description`**: imperative or noun-phrase, action-oriented

### Prompt Content Structure

Agent prompts must cover:

1. **Role statement** — one paragraph defining scope and purpose
2. **Primary function** — what the agent does when invoked
3. **Core responsibilities** — bulleted actionable list
4. **Activation triggers** — conditions under which the agent is invoked
5. **Workflows** — named step-by-step procedures the agent follows
6. **Quality standards** — acceptance criteria for agent outputs
7. **Validation scripts** — paths to scripts the agent should run
8. **Related documentation** — spec and doc paths the agent references

### Related Files

Each agent should have corresponding files:

| File | Location | Purpose |
|------|----------|---------|
| Agent definition | `.github/agents/<name>.agent.md` | Entry point |
| Prompt workflow | `.github/prompts/<name>.prompt.md` | Detailed prompt for Copilot |
| Skill | `.github/skills/<name>/SKILL.md` | Executable capability |

### Access Restrictions

The `.github/agents/` directory contains system-level coordination files. Agent files are:

- ✅ Accessible during meta-intelligence and onboarding tasks
- ❌ Not required reading during normal coding tasks
- Prevents context contamination during day-to-day development

## Validation

Before committing an agent file:

1. YAML frontmatter is valid and parseable
2. All required fields are present
3. `name` matches the file stem in kebab-case
4. `description` is 1–256 characters
5. `prompt` covers all required content sections
6. Corresponding prompt file exists (if applicable)

```bash
# Validate YAML frontmatter
python -c "import yaml; yaml.safe_load(open('.github/agents/<name>.agent.md').read().split('---')[1])"
```

## References

→ **Framework**: `.github/docs/agent-intelligence-framework.md`
→ **Agent instructions**: `.github/instructions/agents.instructions.md`
→ **Prompt spec**: `.github/specs/prompts.md`
→ **Skill spec**: `.github/specs/skills.md`
→ **Repository spec**: `.github/specs/repository.md`
