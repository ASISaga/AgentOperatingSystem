# Task List: [FEATURE NAME]

**Feature Number**: [NNN]
**Branch**: [NNN-feature-slug]
**Generated**: [YYYY-MM-DD]
**Plan**: [NNN-feature-slug/plan.md](plan.md)

---

## Summary

| Metric | Value |
|--------|-------|
| Total tasks | [N] |
| Parallel groups | [N] |
| Critical path depth | [N sequential stages] |

---

## Legend

- `[P]` — Parallel: can run concurrently with other `[P]` tasks in the same group
- `[ ]` — Not started
- `[x]` — Complete
- Dependency: listed explicitly as `(depends on task-NNN)`

---

## Parallel Group 0: Setup

> Tasks that can be done immediately with no dependencies.

- [ ] [P] task-001: Install and pin dependencies
  - Input: `research.md` library choices
  - Output: Updated `pyproject.toml` (or equivalent), lockfile
  - Test: `pip install -e ".[dev]"` succeeds; `import <package_name>` works

- [ ] [P] task-002: Create directory structure
  - Input: Plan phase structure
  - Output: Required directories and placeholder files created
  - Test: All directories exist; no import errors

---

## Parallel Group 1: Contracts and Schemas

> Define contracts and schemas before writing any implementation code.

- [ ] [P] task-003: Define API contracts
  - Input: Acceptance criteria from `spec.md`
  - Output: `contracts/api.md` with all endpoints/events
  - Test: Contract document reviewed and approved by team

- [ ] [P] task-004: Define data model schemas
  - Input: User stories from `spec.md`
  - Output: `data-model.md` with all entities and relationships
  - Test: All entities trace back to a user story

---

## Sequential: Contract Tests (depends on Group 1)

- [ ] task-005: Write contract tests (depends on task-003)
  - Input: `contracts/api.md`
  - Output: Failing contract test file
  - Test: Tests run and **fail** (Red phase confirmed)

- [ ] task-006: Write integration tests (depends on task-003, task-004)
  - Input: `contracts/api.md`, `data-model.md`
  - Output: Failing integration test file
  - Test: Tests run and **fail** (Red phase confirmed)

---

## Sequential: Implementation (depends on contract tests approved)

> Tests must be reviewed and approved before starting implementation.

- [ ] task-007: Implement [core component] (depends on task-005, task-006)
  - Input: Approved test files, `contracts/api.md`
  - Output: Source code that passes contract tests
  - Test: `pytest tests/contract/` passes (Green phase)

- [ ] task-008: Implement [secondary component] (depends on task-007)
  - Input: task-007 output
  - Output: Source code that passes integration tests
  - Test: `pytest tests/integration/` passes

---

## Sequential: Validation (depends on all implementation)

- [ ] task-009: End-to-end validation (depends on task-007, task-008)
  - Input: `quickstart.md` validation scenarios
  - Output: All scenarios verified
  - Test: Each quickstart scenario passes manually

- [ ] task-010: Non-functional validation (depends on task-009)
  - Input: NFRs from `spec.md`
  - Output: Performance/security validation report
  - Test: All NFR targets met (response time, throughput, etc.)

---

## Task Quality Checklist

- [ ] Every task is atomic (single, verifiable deliverable)
- [ ] Every task traces to a spec user story or plan phase
- [ ] Every task has an explicit verification step
- [ ] No task is estimated at >4 hours (break down if needed)
- [ ] Contract tests are listed before implementation tasks
- [ ] All `[NEEDS CLARIFICATION]` resolved before tasks executed
