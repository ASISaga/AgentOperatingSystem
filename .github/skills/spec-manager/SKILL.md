---
name: spec-manager
description: Manage specification-driven development workflow for .github/specs/. Create, validate, and update feature specifications, implementation plans, and task lists. Use when creating or updating specs for the repository using the Copilot agent intelligence system.
license: MIT
metadata:
  author: ASISaga
  version: "1.1"
  category: specification
  role: specification-engineer
allowed-tools: Bash(git:*) Bash(mkdir:*) Bash(cp:*) Read Edit Create
---

# Spec Manager

**Role**: Specification Engineer for SDD Workflow
**Scope**: `specs/`, `.github/specs/`, `.github/templates/`
**Version**: 1.1

## Purpose

Implement the Specification-Driven Development (SDD) workflow through three agent-driven stages that transform plain-language descriptions into structured, executable specifications.

→ **SDD principles**: `.github/specs/spec-driven-development.md`
→ **Full methodology**: `.github/docs/spec-driven.md`

## When to Use This Skill

Activate when:
- A new feature needs a structured specification
- An existing spec needs to be validated or refined
- An implementation plan needs to be generated from a spec
- A task list needs to be derived from a plan

## Three SDD Workflows

| Stage | Prompt | Output |
|-------|--------|--------|
| 1. Specify | `spec-create.prompt.md` | `specs/NNN-slug/spec.md` |
| 2. Plan | `spec-plan.prompt.md` | `plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md` |
| 3. Tasks | `spec-tasks.prompt.md` | `specs/NNN-slug/tasks.md` |

## Core Principles (from SDD)

**Spec-First**: Specifications drive code, not the reverse
**Clarify, Don't Guess**: Mark all ambiguities with `[NEEDS CLARIFICATION]`
**Constitutional Gates**: Enforce Articles III, VII, VIII, IX before planning
**Test-First Ordering**: Contract tests → integration tests → implementation

## Validation Scripts

### 1. Spec Validation

```bash
./.github/skills/spec-manager/scripts/validate-spec.sh specs/<NNN>-<slug>/spec.md

# Checks:
# - No [NEEDS CLARIFICATION] markers remain
# - Required sections are present
# - User stories have role/goal/benefit
# - Acceptance criteria are measurable
```

### 2. List Specs

```bash
./.github/skills/spec-manager/scripts/list-specs.sh

# Shows:
# - All feature directories in specs/
# - Status of spec.md, plan.md, tasks.md
# - Next available feature number
```

### 3. Create Feature Branch

```bash
./.github/skills/spec-manager/scripts/create-feature-branch.sh "<description>"

# Creates:
# - git branch NNN-kebab-slug
# - specs/NNN-kebab-slug/ directory
```

## Validation

**Before committing spec changes:**

```bash
# Validate spec completeness
./.github/skills/spec-manager/scripts/validate-spec.sh specs/<NNN>-<slug>/spec.md

# List all specs and their status
./.github/skills/spec-manager/scripts/list-specs.sh
```

## Resources

→ `.github/specs/spec-driven-development.md` — SDD principles and workflow
→ `.github/specs/prompts.md` — Prompt file specification
→ `.github/specs/agents.md` — Agent file specification
→ `.github/docs/spec-driven.md` — Full SDD methodology
→ `.github/agents/spec-manager.agent.md` — Agent definition
→ `.github/prompts/spec-create.prompt.md` — Create workflow
→ `.github/prompts/spec-plan.prompt.md` — Plan workflow
→ `.github/prompts/spec-tasks.prompt.md` — Tasks workflow

---

**Version History**:
- **v1.1** (2026-03-07): Adapted to Copilot agent meta-intelligence system; removed speckit command references
- **v1.0** (2026-03-07): Initial spec manager skill
