---
description: "Derives an executable task list from an implementation plan: reads plan.md and supporting docs, parallelises independent tasks, and writes tasks.md ready for execution by the coding agent"
name: "spec_tasks"
agent: "agent"
model: "Auto"
tools: ['*']
---

# Spec Tasks — Task List Workflow

**Version**: 1.0.0
**Last Updated**: 2026-03-07

## Role

Analyse an implementation plan and its supporting documents to produce a concrete, executable task list. Every task must be precise enough for the coding agent or a developer to execute without further clarification. Independent tasks are marked for parallelisation.

## Activation

Invoke this prompt when a feature plan exists and is ready for task derivation. Typical triggers:
- "Generate tasks for feature NNN"
- "Create task list for NNN-slug"
- "Break down the plan for …"

> **Note**: Tasks marked `[P]` in the output are **parallel** — they have no dependencies on each other and can be executed concurrently within the same parallel group.

## Pre-condition Check

Before generating tasks, verify:
1. `specs/<NNN>-<slug>/plan.md` exists
2. Constitutional gates were evaluated in `plan.md` (Phase -1 section present)
3. `specs/<NNN>-<slug>/contracts/` exists with at least one contract file

If `plan.md` is missing, stop and direct the user to the **Spec Plan** prompt first.

## Workflow

### Step 1: Parse Inputs

Read all available documents in the feature directory:

| File | What it contributes |
|------|---------------------|
| `plan.md` | Phases, technology decisions, implementation approach (required) |
| `data-model.md` | Entity definitions → model/schema tasks |
| `contracts/api.md` | API contracts → endpoint/handler tasks |
| `research.md` | Library choices → dependency installation tasks |
| `quickstart.md` | Validation scenarios → end-to-end test tasks |

### Step 2: Derive Tasks

Convert each document into atomic tasks:

**From `contracts/`**:
- One implementation task per API endpoint or event handler
- One contract test task per endpoint (must precede implementation)

**From `data-model.md`**:
- One schema/model creation task per entity
- One migration task if database schema changes are needed

**From `plan.md` phases**:
- One task per phase deliverable
- Setup and configuration tasks from Phase 0
- Integration tasks from final phases

**Always include**:
- Dependency installation task (from `research.md` choices)
- Contract tests before any implementation tasks (Article III)
- Integration test tasks
- End-to-end validation task (from `quickstart.md`)

### Step 3: Apply Test-First Ordering (SDD Article III)

Tasks within each feature area must follow this order:

```
1. [contract tests]   Write and approve contract tests (Red phase)
2. [integration tests] Write integration tests (Red phase)
3. [implementation]   Write source code to make tests pass
4. [e2e tests]        Write end-to-end tests
5. [validation]       Run full test suite; verify NFRs
```

### Step 4: Parallelisation Analysis

Mark tasks with no mutual dependencies as `[P]`:

```
## Parallel Group A — no dependencies
- [P] task-A1: Create User entity schema
- [P] task-A2: Create Order entity schema
- [P] task-A3: Install dependencies from research.md

## Sequential — depends on Group A
- task-B1: Create database migration (depends on task-A1, task-A2)
```

Rules:
- Tasks in the same parallel group have zero dependencies on each other
- A task belongs to exactly one group
- Groups are ordered by dependency chain (critical path)

### Step 5: Create tasks.md

Using `.github/templates/tasks.md` as structure, create `specs/<NNN>-<slug>/tasks.md`.

Each task entry:
```markdown
- [ ] [P] task-NNN: <verb> <object> — <rationale linking to spec/plan>
  - Input: <what is needed>
  - Output: <what is produced>
  - Test: <how to verify completion>
```

### Step 6: Validate

```bash
./.github/skills/spec-manager/scripts/validate-spec.sh specs/<NNN>-<slug>/tasks.md
```

## Output

```
specs/<NNN>-<slug>/
└── tasks.md   ← Executable task list with parallel groups
```

Report to the user:
- Total tasks generated
- Parallel groups identified
- Critical path length (sequential stages)
- Next step: review `tasks.md` and begin execution with the coding agent

## Task Quality Standards

Every task must be:
- **Atomic**: Single, verifiable deliverable
- **Traceable**: Links to a spec user story or plan phase
- **Testable**: Has an explicit verification step
- **Sized**: Completable in ≤4 hours by one person

Reject vague tasks like "implement the feature" — break them into specific, verifiable actions.

## Related Documentation

→ **SDD principles**: `.github/specs/spec-driven-development.md`
→ **Full methodology**: `.github/docs/spec-driven.md`
→ **Spec manager agent**: `.github/agents/spec-manager.agent.md`
→ **Create workflow**: `.github/prompts/spec-create.prompt.md`
→ **Plan workflow**: `.github/prompts/spec-plan.prompt.md`
