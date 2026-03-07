# Agent Onboarding & Training

**Last Updated**: 2026-03-07  
**Audience**: New agents, contributors learning the system

## Overview

Structured onboarding path for new agents (AI or human) joining the BusinessInfinity agent ecosystem.

## Onboarding Checklist

### Phase 1: Foundation (Required)

- [ ] Read `.github/copilot-instructions.md` — High-level architecture
- [ ] Review directory structure in `.github/` (instructions vs specs vs docs)
- [ ] Read `.github/docs/agent-philosophy.md` — Core principles

### Phase 2: Specifications (Required)

- [ ] Read `.github/specs/repository.md` — Repository role, tech stack, design principles
- [ ] Read `.github/specs/workflows.md` — Business workflow patterns
- [ ] Read `.github/specs/agent-intelligence-framework.md` — Complete framework

### Phase 3: Agent System (Required)

- [ ] Review agents in `.github/agents/`, prompts in `.github/prompts/`, skills in `.github/skills/`
- [ ] Read `.github/specs/agents.md` — Agent file conventions
- [ ] Read `.github/specs/prompts.md` — Prompt file conventions
- [ ] Read `.github/specs/skills.md` — Skill file conventions
- [ ] Read `.github/specs/instructions.md` — Instruction file conventions

### Phase 4: Workflows (Required)

- [ ] Read `.github/docs/decision-matrices.md` — Quick decisions
- [ ] Read `.github/docs/agent-workflows.md` — Practical examples
- [ ] Run `pytest tests/ -v` and validation scripts to understand checks

### Phase 5: Quality & Evolution (Recommended)

- [ ] Read `.github/docs/agent-metrics.md` — Quality measurement
- [ ] Read `.github/docs/dogfooding-guide.md` — Self-improvement
- [ ] Run `./.github/skills/agent-evolution-agent/scripts/audit-agent-quality.sh`

## Training Scenarios

### Scenario 1: Adding a New Workflow

**Setup**: A new business process (e.g., `risk-assessment`) needs to be orchestrated.

<details>
<summary>Answer</summary>

1. Check `.github/specs/workflows.md` to see if existing patterns apply.
2. Use `c_suite_orchestration` template — it encapsulates the select → filter → orchestrate pattern.
3. Choose the appropriate variant (perpetual / hierarchical / sequential) based on the decision matrix.
4. Run `pytest tests/ -v` after adding the workflow.

→ `.github/docs/decision-matrices.md`
</details>

### Scenario 2: Agent File Missing Spec References

**Setup**: An agent file has less than 3 spec references.

<details>
<summary>Answer</summary>

1. Run `./.github/skills/agent-evolution-agent/scripts/recommend-improvements.sh`
2. Identify which `.github/specs/` files are relevant to the agent's domain
3. Add references to the "Related Documentation" section
4. Re-run audit to verify improvement

→ `.github/docs/dogfooding-guide.md`
</details>

### Scenario 3: Creating a Feature Specification

**Setup**: New feature request arrives without technical details.

<details>
<summary>Answer</summary>

1. Invoke the Spec Manager Agent (or use `spec-create.prompt.md` directly)
2. Transform the description into `specs/NNN-slug/spec.md`
3. Mark all ambiguities with `[NEEDS CLARIFICATION]`
4. Validate: `./.github/skills/spec-manager/scripts/validate-spec.sh`

→ `.github/specs/spec-driven-development.md`
</details>

## Agent Role Quick Guide

| Agent | Focus | Key Files |
|-------|-------|-----------|
| Agent Evolution | Quality metrics, duplication, spec coverage | `.github/docs/dogfooding-guide.md` |
| Documentation Manager | Doc structure, links, metadata, archival | `.github/skills/documentation-manager-agent/SKILL.md` |
| Repository Onboarding | Bootstrap agent system in new repos | `.github/skills/repository-onboarding/SKILL.md` |
| Spec Manager | SDD workflow: Specify → Plan → Tasks | `.github/skills/spec-manager/SKILL.md` |

## Key Resources

| Resource | Location |
|----------|----------|
| Repository spec | `.github/specs/repository.md` |
| Workflow patterns | `.github/specs/workflows.md` |
| Python standards | `.github/instructions/python.instructions.md` |
| Azure Functions patterns | `.github/instructions/azure-functions.instructions.md` |
| All tool commands | `.github/docs/conventional-tools.md` |
| Dogfooding guide | `.github/docs/dogfooding-guide.md` |

---

**Version**: 2.0 - Adapted to BusinessInfinity  
**Last Updated**: 2026-03-07  
**Purpose**: Structured onboarding and training for new agents
