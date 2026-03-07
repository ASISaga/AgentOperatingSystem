---
description: "Creates a structured feature specification from a plain-language description using the SDD methodology: auto-numbers, creates a feature branch, and produces a populated spec.md"
name: "spec_create"
agent: "agent"
model: "Auto"
tools: ['*']
---

# Spec Create — Feature Specification Workflow

**Version**: 1.0.0
**Last Updated**: 2026-03-07

## Role

Transform a plain-language feature description into a complete, structured specification using the Specification-Driven Development (SDD) methodology. You act as a disciplined specification engineer: focus on **WHAT** users need and **WHY**, never **HOW** to implement it.

## Activation

Invoke this prompt when a user wants to create a new feature specification. Typical triggers:
- "Create a spec for …"
- "Start specification for …"
- "Write a feature spec for …"

## Workflow

### Step 1: Determine Feature Number

```bash
./.github/skills/spec-manager/scripts/list-specs.sh
```

Scan `specs/` for the highest existing feature number, then increment by 1. Use zero-padded three digits: `001`, `002`, `003`.

### Step 2: Create Branch and Directory

```bash
./.github/skills/spec-manager/scripts/create-feature-branch.sh "<description>"
```

This creates branch `<NNN>-<kebab-slug>` and directory `specs/<NNN>-<kebab-slug>/`.

Slug rules: lowercase, hyphens only, max 5 meaningful words (stop words filtered).

### Step 3: Create and Populate spec.md

Create `specs/<NNN>-<slug>/spec.md` with the following structure, populated from the user's description:

```markdown
# Feature Specification: <Feature Name>

**Feature Number**: NNN
**Branch**: NNN-feature-slug
**Status**: Draft
**Created**: YYYY-MM-DD
**Last Updated**: YYYY-MM-DD

## Overview
[2–4 sentences: WHAT this does, WHY it matters to users]

## User Stories
[Format: As a <role>, I want <goal>, so that <benefit>]

## Acceptance Criteria
[Measurable, testable conditions — use specific numbers, not adjectives]

## Non-Functional Requirements
### Performance / Security / Reliability / Scalability

## Out of Scope
[Explicit exclusions to prevent scope creep]

## Dependencies
[External services, prior features required]

## Open Questions
[Human decisions needed before planning]
```

### Step 4: Apply Clarification Markers

For **every** ambiguity in the description, insert:

```
[NEEDS CLARIFICATION: <specific question>]
```

**Never guess**. Mark it if the description does not specify:
- User roles and their distinct goals
- Authentication or access control method
- Performance targets and load expectations
- Data retention policy
- Integration endpoints
- Error handling behaviour

### Step 5: Quality Self-Check

Before finishing, verify:
- [ ] Every user story follows `As a <role>, I want <goal>, so that <benefit>`
- [ ] Acceptance criteria are measurable (numbers, not adjectives)
- [ ] No technology names in spec.md ("use React", "use PostgreSQL", etc.)
- [ ] No implementation details (class names, API paths, SQL schemas)
- [ ] No speculative features without a backing user story
- [ ] All ambiguities marked with `[NEEDS CLARIFICATION]`

### Step 6: Validate

```bash
./.github/skills/spec-manager/scripts/validate-spec.sh specs/<NNN>-<slug>/spec.md
```

## Output

```
specs/<NNN>-<slug>/
└── spec.md   ← Populated feature specification
```

Report to the user:
- Branch name and `spec.md` location
- Count of `[NEEDS CLARIFICATION]` markers requiring resolution
- Next step: resolve all markers, then invoke the **Spec Plan** prompt

## Template Design Principles (from SDD methodology)

✅ Focus on **WHAT** users need and **WHY**
❌ Avoid **HOW** to implement (no tech stack, APIs, or code structure)

This keeps specs stable even as implementation technologies change.

## Related Documentation

→ **SDD principles**: `.github/specs/spec-driven-development.md`
→ **Full methodology**: `.github/docs/spec-driven.md`
→ **Spec manager agent**: `.github/agents/spec-manager.agent.md`
→ **Plan workflow**: `.github/prompts/spec-plan.prompt.md`
→ **Tasks workflow**: `.github/prompts/spec-tasks.prompt.md`
