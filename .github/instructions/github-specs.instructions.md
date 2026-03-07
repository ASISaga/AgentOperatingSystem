---
applyTo: ".github/specs/*.md"
description: "Standards for specification files in .github/specs/ including spec-driven development (SDD) workflow"
---

# Specification Files Standards

## Purpose

Specification files in `.github/specs/` contain **detailed patterns and frameworks** that instruction files reference. They define the "what" and "how" of systems.

Specifications are created and updated using the **Spec Manager Agent** and its three SDD workflows.

→ **SDD workflow**: `.github/specs/spec-driven-development.md`
→ **Spec manager agent**: `.github/agents/spec-manager.agent.md`

## Spec-Driven Development (SDD) Workflow

New feature specifications are created through the Copilot agent intelligence system:

| Stage | Prompt | Output |
|-------|--------|--------|
| 1. Specify | `spec-create.prompt.md` | `specs/NNN-slug/spec.md` |
| 2. Plan | `spec-plan.prompt.md` | `plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md` |
| 3. Tasks | `spec-tasks.prompt.md` | `specs/NNN-slug/tasks.md` |

All specs created by the agent are placed in `specs/<NNN>-<slug>/`. Specs in `.github/specs/` document the agent intelligence system itself and follow the standard format below.

## File Naming

- Use kebab-case: `system-name.md`
- Be descriptive: `ontological-design-system.md` not `ontology.md`
- Include version if needed: `agent-framework-v2.md`

## Content Structure

```markdown
# Specification Title

**Version**: X.Y.Z  
**Status**: Draft | Active | Deprecated  
**Last Updated**: YYYY-MM-DD

## Overview
[Brief description of what this specifies]

## Scope
[What's included and excluded]

## Specification
[Detailed patterns, frameworks, requirements]

## Examples
[Code examples and use cases]

## Validation
[How to verify compliance]

## References
[Related specs and docs]
```

## Content Guidelines

✅ **DO Include:**
- Detailed technical specifications
- Complete frameworks and patterns
- Code examples and templates
- Architecture diagrams
- Validation criteria

❌ **DON'T Include:**
- Step-by-step tutorials (belong in `.github/docs/`)
- Path-specific coding standards (belong in `.github/instructions/`)
- Project-specific implementations (reference from specs)

## Cross-References

Specs should be:
- **Referenced from**: Instruction files, documentation files, copilot-instructions.md
- **Never duplicated in**: Instruction files or copilot-instructions.md

## Validation

Before committing:
1. Follows naming convention
2. Has proper version/status/date
3. Clear scope and specification sections
4. Examples are correct and tested
5. No duplication with docs or instructions

## Related Documentation

→ **SDD spec**: `.github/specs/spec-driven-development.md` - SDD principles and agent workflows
→ **Agent spec**: `.github/specs/agents.md` - Agent file specification
→ **Prompt spec**: `.github/specs/prompts.md` - Prompt file specification
→ **Skill spec**: `.github/specs/skills.md` - Skill file specification
→ **Instructions spec**: `.github/specs/instructions.md` - Instruction file specification
→ **Framework**: `.github/docs/agent-intelligence-framework.md` - Complete system framework

---

**Version**: 1.4 - Updated references to use dedicated spec files
**Last Updated**: 2026-03-07
