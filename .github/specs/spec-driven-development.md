# Specification-Driven Development (SDD)

**Version**: 1.1.0
**Status**: Active
**Last Updated**: 2026-03-07

## Overview

Specification-Driven Development (SDD) inverts the traditional relationship between specs and code: specifications are the primary artifact; code is their generated expression. This spec defines how SDD principles are practised in this repository through the GitHub Copilot coding agent meta-intelligence system.

→ **Full methodology**: `.github/docs/spec-driven.md`

## Scope

- SDD principles adopted for the `.github/specs/` directory
- Three agent-driven SDD workflows: Specify → Plan → Tasks
- Constitutional gates, clarification discipline, and quality standards
- Integration with the Copilot agent intelligence system

## The Three SDD Workflows

SDD is implemented through the **Spec Manager Agent** and three dedicated prompt workflows. Each stage produces a structured document that gates the next stage.

### Stage 1 — Specify (`spec-create.prompt.md`)

Transforms a plain-language description into a complete, structured feature specification:

1. **Auto-number**: Determine next feature number (`list-specs.sh`)
2. **Branch**: Create `NNN-slug` branch and `specs/NNN-slug/` directory (`create-feature-branch.sh`)
3. **Specify**: Create `specs/NNN-slug/spec.md` with user stories, acceptance criteria, NFRs
4. **Clarify**: Mark every ambiguity with `[NEEDS CLARIFICATION: <question>]` — never guess

### Stage 2 — Plan (`spec-plan.prompt.md`)

Reads `spec.md` (all clarification markers resolved) and produces a full implementation plan:

1. **Gate**: Run Phase -1 constitutional gates (Articles III, VII, VIII, IX)
2. **Research**: Create `research.md` — library options, benchmarks, security, SDK constraints
3. **Model**: Create `data-model.md` — entities, fields, relationships, all traced to user stories
4. **Contracts**: Create `contracts/api.md` — API endpoints/events before any implementation
5. **Plan**: Create `plan.md` — technology choices linked to requirements, implementation phases
6. **Quickstart**: Create `quickstart.md` — key validation scenarios

### Stage 3 — Tasks (`spec-tasks.prompt.md`)

Reads `plan.md` and supporting documents → derives an executable task list:

1. **Parse**: Extract tasks from contracts, data model, plan phases
2. **Order**: Apply test-first ordering (contract tests → integration → implementation → e2e)
3. **Parallelise**: Mark independent tasks `[P]` and group safe parallel clusters
4. **Output**: Create `specs/NNN-slug/tasks.md` ready for coding agent execution

## Feature Directory Structure

```
specs/
└── NNN-feature-slug/
    ├── spec.md                      ← Feature specification (Stage 1)
    ├── plan.md                      ← Implementation plan (Stage 2)
    ├── research.md                  ← Library/API research (Stage 2)
    ├── data-model.md                ← Entity schemas (Stage 2)
    ├── contracts/                   ← API/event contracts (Stage 2)
    │   └── api.md
    ├── quickstart.md                ← Key validation scenarios (Stage 2)
    ├── tasks.md                     ← Executable task list (Stage 3)
    └── implementation-details/      ← Detailed technical content extracted from plan.md
        └── [component]-details.md
```

## Specification Templates

Used as structural guides by the agent when creating documents:

| Template | Stage | Purpose |
|----------|-------|---------|
| `.github/templates/plan.md` | Plan | Implementation plan with Phase -1 gates |
| `.github/templates/tasks.md` | Tasks | Task list with parallelisation groups |
| `.github/templates/research.md` | Plan | Library research, benchmarks, security |
| `.github/templates/data-model.md` | Plan | Entity schemas, relationships, validation |

## Constitutional Principles (adopted from SDD)

These articles are enforced through Phase -1 gates in the Plan stage.

| Article | Principle | Enforcement |
|---------|-----------|-------------|
| I | Library-First: every feature starts as a standalone library | Spec checklist |
| II | CLI Interface: every library exposes a CLI (stdin→stdout, JSON) | Plan gate |
| III | Test-First: failing tests approved before any implementation code | Phase -1 gate |
| VII | Simplicity: ≤3 projects for initial implementation | Simplicity gate |
| VIII | Anti-Abstraction: use framework directly; single model representation | Anti-abstraction gate |
| IX | Integration-First: real services over mocks; contract tests before code | Integration gate |

## Clarification Markers

All ambiguities in a specification **must** be surfaced with:

```
[NEEDS CLARIFICATION: <specific question about the missing or ambiguous detail>]
```

**Never guess**. Specs with unresolved markers are blocked from proceeding to the Plan stage.

## Spec Quality Gates

A spec is ready to proceed to Stage 2 (Plan) when:

- [ ] No `[NEEDS CLARIFICATION]` markers remain
- [ ] All user stories follow `As a <role>, I want <goal>, so that <benefit>`
- [ ] Acceptance criteria are measurable and testable (numbers, not adjectives)
- [ ] Non-functional requirements have specific targets
- [ ] No implementation details in spec.md (no tech stack, APIs, or code structure)
- [ ] No speculative or "might need" features

## Validation

```bash
# Validate a spec or plan file for completeness
./.github/skills/spec-manager/scripts/validate-spec.sh specs/<NNN>-<slug>/spec.md

# List all feature specs and their status
./.github/skills/spec-manager/scripts/list-specs.sh

# Create a feature branch and directory for a new spec
./.github/skills/spec-manager/scripts/create-feature-branch.sh "<description>"
```

## References

→ **Full SDD methodology**: `.github/docs/spec-driven.md`
→ **Spec manager agent**: `.github/agents/spec-manager.agent.md`
→ **Create workflow**: `.github/prompts/spec-create.prompt.md`
→ **Plan workflow**: `.github/prompts/spec-plan.prompt.md`
→ **Tasks workflow**: `.github/prompts/spec-tasks.prompt.md`
→ **Agent framework**: `.github/specs/agent-intelligence-framework.md`
→ **Repository spec**: `.github/specs/repository.md`
