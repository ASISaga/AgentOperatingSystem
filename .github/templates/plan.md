# Implementation Plan: [FEATURE NAME]

**Feature Number**: [NNN]
**Branch**: [NNN-feature-slug]
**Status**: Draft | In Review | Approved
**Created**: [YYYY-MM-DD]
**Last Updated**: [YYYY-MM-DD]
**Spec**: [NNN-feature-slug/spec.md](spec.md)

---

> **IMPORTANT**: This plan should remain high-level and readable.
> Any code samples, detailed algorithms, or extensive technical specifications
> must be placed in `implementation-details/` files.

## Phase -1: Constitutional Gates

All gates must pass before implementation begins. Document exceptions in Complexity Tracking.

### Simplicity Gate (Article VII)

- [ ] Using ≤3 projects for initial implementation?
- [ ] No future-proofing beyond stated requirements?
- [ ] All complexity justified by a specific user story?

### Anti-Abstraction Gate (Article VIII)

- [ ] Using framework features directly rather than wrapping them?
- [ ] Single model representation (no DTO proliferation)?
- [ ] Each abstraction layer has documented concrete benefit?

### Integration-First Gate (Article IX)

- [ ] Contracts defined before implementation starts?
- [ ] Contract tests written before source code?
- [ ] Real services preferred over mocks in tests?

### Test-First Gate (Article III)

- [ ] Tests will be written and approved before implementation code?
- [ ] Test scenarios derived from acceptance criteria in spec.md?
- [ ] Red phase (failing tests) confirmed before implementation?

### Complexity Tracking

> Document any gate exceptions here with explicit rationale.

_No exceptions at this time._

---

## Technology Choices

> Each choice must link to a specific requirement or user story.

| Decision | Choice | Rationale | Requirement |
|----------|--------|-----------|-------------|
| [Component] | [Technology] | [Why this over alternatives] | [User story / criterion ref] |

## Architecture Overview

> High-level description of how the feature fits into the existing system.
> No code — use diagrams or prose.

[Describe the architectural approach and how it integrates with existing components]

→ See `.github/specs/repository.md` for existing architecture context.

## Implementation Phases

> Each phase must have clear prerequisites and deliverables.
> No speculative phases or "might be needed" work.

### Phase 0: Setup

**Prerequisites**: Constitutional gates passed, contracts defined
**Deliverables**:
- [ ] Dependencies installed and verified
- [ ] Development environment configured

### Phase 1: Contracts and Tests

**Prerequisites**: Phase 0 complete
**Deliverables**:
- [ ] API contracts defined in `contracts/`
- [ ] Contract tests written (failing — Red phase)
- [ ] Integration tests written (failing)

### Phase 2: Core Implementation

**Prerequisites**: Phase 1 complete, tests reviewed and approved
**Deliverables**:
- [ ] Source code written to pass contract tests
- [ ] Source code written to pass integration tests

### Phase 3: Validation

**Prerequisites**: Phase 2 complete, all tests green
**Deliverables**:
- [ ] End-to-end validation against quickstart.md scenarios
- [ ] Non-functional requirements verified (performance, security)
- [ ] Documentation updated

## Supporting Documents

| Document | Purpose | Status |
|----------|---------|--------|
| [research.md](research.md) | Library and API research | [ ] |
| [data-model.md](data-model.md) | Entity schemas | [ ] |
| [contracts/api.md](contracts/api.md) | API / event contracts | [ ] |
| [quickstart.md](quickstart.md) | Validation scenarios | [ ] |

## File Creation Order

> Strictly follow test-first ordering (Article III):

1. `contracts/` — API specifications
2. Test files: contract tests → integration tests → e2e → unit
3. Source files to make tests pass

---

## Plan Quality Checklist

- [ ] Every technology choice linked to a specific requirement
- [ ] All phases have clear prerequisites and deliverables
- [ ] No speculative phases or "might need" items
- [ ] Gate exceptions documented with rationale
- [ ] Supporting documents listed
