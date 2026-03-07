# Prompt Files Specification

**Version**: 1.0.0
**Status**: Active
**Last Updated**: 2026-03-07

## Overview

Specifies the format, structure, and conventions for GitHub Copilot prompt files (`*.prompt.md`) stored in `.github/prompts/`.

## Scope

- YAML frontmatter requirements for `.prompt.md` files
- Required fields and naming conventions
- Body structure and content guidelines
- Tool integration patterns

## Specification

### File Format

Every prompt file must begin with valid YAML frontmatter:

```yaml
---
description: "Brief agent purpose (1–256 chars)"
name: "agent_name"         # snake_case
agent: "agent"             # or "ask", "edit", or custom mode
model: "claude-3-5-sonnet-20241022"
tools: ['*']               # or explicit list of allowed tools
---
```

### Required Fields

| Field | Type | Constraint |
|-------|------|-----------|
| `description` | string | 1–256 characters; purpose summary |
| `name` | string | snake_case; discoverable, action-oriented |
| `agent` | string | `"agent"`, `"ask"`, `"edit"`, or custom |
| `model` | string | LLM model identifier |
| `tools` | list | `['*']` for all tools, or scoped list |

### Naming Conventions

- **File**: `<agent-name>.prompt.md` (kebab-case)
- **`name` field**: snake_case matching the agent concept (`spec_manager`)
- **`description`**: concise, discoverable, imperative or noun-phrase

### Body Structure

Prompt files must follow this section order:

1. **Role and purpose** — one paragraph defining scope
2. **Core responsibilities** — actionable bulleted list
3. **When to use** — explicit activation triggers
4. **Workflows and examples** — named step-by-step procedures
5. **Tool integration** — bash commands and validation scripts
6. **Related documentation** — spec and doc cross-references

### Tool Integration

Reference existing tools; never reimplement:

```bash
# Run all tests
pytest tests/ -v

# Run lint
pylint src/

# Validation scripts
./.github/skills/[skill-name]/scripts/validate-*.sh
```

Declare tool access in frontmatter using scoped patterns where possible:

```yaml
tools: ['bash', 'read', 'edit', 'grep', 'create']
```

### Keep Focused

Prompt files must be lean:

- Delegate detailed framework specifications to `.github/specs/`
- Delegate implementation guides to `.github/docs/`
- Eliminate redundancy with `copilot-instructions.md`

## Validation

Before committing a prompt file:

1. YAML frontmatter is valid and parseable
2. All required fields are present
3. `name` is snake_case
4. `description` is 1–256 characters
5. Body follows the required section order
6. No duplication with `copilot-instructions.md`

```bash
# Validate YAML frontmatter
python -c "import yaml; yaml.safe_load(open('.github/prompts/<name>.prompt.md').read().split('---')[1])"
```

## References

→ **Framework**: `.github/docs/agent-intelligence-framework.md`
→ **Prompt instructions**: `.github/instructions/prompts.instructions.md`
→ **Agent spec**: `.github/specs/agents.md`
→ **Skill spec**: `.github/specs/skills.md`
→ **Repository spec**: `.github/specs/repository.md`
