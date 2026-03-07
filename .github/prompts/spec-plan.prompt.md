---
description: "Generates a comprehensive implementation plan from an existing feature spec: runs constitutional gates, translates requirements to technical architecture, and produces research, data-model, contracts, and quickstart documents"
name: "spec_plan"
agent: "agent"
model: "Auto"
tools: ['*']
---

# Spec Plan — Implementation Plan Workflow

**Version**: 1.0.0
**Last Updated**: 2026-03-07

## Role

Read an existing `spec.md` and generate a full implementation plan that bridges business requirements and technical architecture. Every technical decision must trace back to a specific user story or acceptance criterion. Constitutional principles are enforced through **Phase -1 gates** — a pre-implementation checklist run before any technical content is written, ensuring architectural constraints are validated upfront.

## Activation

Invoke this prompt when a feature spec exists and is ready for planning. Typical triggers:
- "Plan the spec for …"
- "Generate implementation plan for feature NNN"
- "Plan feature NNN-slug"

Optionally provide technical hints: "using WebSocket for real-time, PostgreSQL for persistence".

## Pre-condition Check

Before generating the plan, verify:

1. `specs/<NNN>-<slug>/spec.md` exists
2. No `[NEEDS CLARIFICATION]` markers remain in `spec.md`
3. All acceptance criteria are measurable

If any condition fails, stop and report what must be resolved first. Direct the user to the **Spec Create** prompt if `spec.md` is missing.

## Workflow

### Phase -1: Constitutional Gates

Run all gates before writing any plan content. A failed gate must be documented in the Complexity Tracking section of `plan.md`.

#### Simplicity Gate (SDD Article VII)
- [ ] Using ≤3 projects for initial implementation?
- [ ] No future-proofing added beyond stated requirements?
- [ ] All complexity justified by a specific user story?

#### Anti-Abstraction Gate (SDD Article VIII)
- [ ] Using framework features directly rather than wrapping them?
- [ ] Single model representation (no DTO proliferation)?
- [ ] Each abstraction layer justified by concrete benefit?

#### Integration-First Gate (SDD Article IX)
- [ ] Contracts defined before implementation begins?
- [ ] Contract tests will be written before source code?
- [ ] Real services preferred over mocks in tests?

#### Test-First Gate (SDD Article III)
- [ ] Tests will be written and approved before implementation code?
- [ ] Test scenarios derived from acceptance criteria in `spec.md`?
- [ ] Red phase (failing tests) confirmed before implementation?

### Step 1: Read and Analyse Spec

Parse `specs/<NNN>-<slug>/spec.md`:
- Extract user stories with roles, goals, benefits
- Map each story to technical requirements
- Identify data entities, API surface, integration points
- Determine non-functional constraints

### Step 2: Generate research.md

Using `.github/templates/research.md` as structure, create `specs/<NNN>-<slug>/research.md`:
- Evaluate library options for key technical decisions
- Document performance benchmarks relevant to spec NFRs
- Note security implications and known CVEs
- Record constraints from `.github/specs/repository.md` (Python version, Azure Functions, SDK)

### Step 3: Generate data-model.md

Using `.github/templates/data-model.md` as structure, create `specs/<NNN>-<slug>/data-model.md`:
- Define all entities with fields, types, and constraints
- Document entity relationships
- Map each entity back to a user story

### Step 4: Generate contracts/api.md

Define all API contracts before any implementation:
- REST endpoints or Azure Functions HTTP triggers
- Request/response schemas with types
- Error codes and messages
- Service Bus events or WebSocket messages (if applicable)

### Step 5: Create plan.md

Using `.github/templates/plan.md` as structure, create `specs/<NNN>-<slug>/plan.md`:
- Link every technology choice to a specific user story
- Define implementation phases with clear prerequisites
- Extract detailed technical content to `implementation-details/<component>-details.md`
- Keep `plan.md` high-level and readable

### Step 6: Generate quickstart.md

Capture key validation scenarios:
- Happy-path end-to-end scenario
- Critical error paths
- Performance validation approach against spec NFRs

### Step 7: Validate

```bash
./.github/skills/spec-manager/scripts/validate-spec.sh specs/<NNN>-<slug>/plan.md
```

## Output

```
specs/<NNN>-<slug>/
├── plan.md           ← Implementation plan (high-level)
├── research.md       ← Library/API research
├── data-model.md     ← Entity schemas
├── contracts/
│   └── api.md        ← API/event contracts
└── quickstart.md     ← Key validation scenarios
```

Report to the user:
- All files created
- Any constitutional gates that failed (with documented exceptions)
- Next step: review plan, then invoke the **Spec Tasks** prompt

## Plan Quality Standards

`plan.md` must remain navigable. Detailed content goes in separate files:

> Any code samples, detailed algorithms, or extensive technical specifications
> must be placed in `implementation-details/` files, not in `plan.md`.

## File Creation Order (Test-First, SDD Article III)

1. `contracts/` — API specifications first
2. Test files: contract tests → integration tests → e2e → unit
3. Source files to make tests pass

## Related Documentation

→ **SDD principles**: `.github/specs/spec-driven-development.md`
→ **Full methodology**: `.github/docs/spec-driven.md`
→ **Spec manager agent**: `.github/agents/spec-manager.agent.md`
→ **Create workflow**: `.github/prompts/spec-create.prompt.md`
→ **Tasks workflow**: `.github/prompts/spec-tasks.prompt.md`
→ **Repository spec**: `.github/specs/repository.md`
