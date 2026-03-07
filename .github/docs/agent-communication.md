# Agent Communication Protocols

**Last Updated**: 2026-03-07  
**Audience**: All agents, system architects

## Overview

How agents communicate with each other, with human developers, and with the broader ecosystem.

## Communication Channels

| Channel | Purpose | When to Use |
|---------|---------|-------------|
| **Pull Requests** | Propose and review changes | Code, spec, agent, doc changes |
| **GitHub Issues** | Proposals needing community input | Breaking changes, architecture decisions |
| **Code Comments** | Document inline reasoning | Why a decision was made, design intent |
| **Spec Updates** | Keep agents synchronized | After significant system changes to `.github/specs/` |

## Agent Handoff Configuration

Coordination files in `.github/agents/`:
- `agent-handoff.yml` — Workflow transitions between agents
- `agent-coordination.yml` — Agent capabilities and routing
- `quality-thresholds.yml` — Quality gates
- `feature-flags.yml` — System-level toggles

## Agent-to-Agent Protocols

### Agent Evolution → All Agents

1. Agent Evolution runs quality audits and identifies issues
2. Evolution identifies agents with low spec coverage or high duplication
3. Target agent fixes issues based on recommendations
4. Evolution re-runs audit to validate improvement and updates metrics

### Documentation Manager ↔ All Agents

1. Documentation Manager validates doc structure and links
2. Any agent creating docs must follow `.github/instructions/docs.instructions.md`
3. Completed implementation docs move to `docs/archive/implementations/`
4. Single source of truth — no duplicate content

### Spec Manager → Developer

1. Developer describes feature in plain language
2. Spec Manager transforms to structured `spec.md` in `specs/NNN-slug/`
3. Developer resolves `[NEEDS CLARIFICATION]` markers
4. Spec Manager generates `plan.md`, then `tasks.md`
5. Coding agent implements tasks in order

## Agent-to-Human Protocols

### Core Principles

- **DO**: Explain "why," provide examples, reference specs, suggest alternatives
- **DON'T**: Make architectural decisions without referencing `.github/specs/repository.md`

### Proposing Changes

1. Read the relevant spec in `.github/specs/` before proposing
2. Use the SDD workflow for new features: `spec-create.prompt.md`
3. Use a PR for code changes; validate with `pytest tests/ -v && pylint src/`

## Breaking Changes Protocol

1. Open GitHub Issue for discussion
2. Document migration path
3. Update relevant spec in `.github/specs/`
4. Add entry to CHANGELOG

## Conflict Resolution

1. Each agent states position with reasoning, referencing specs/docs
2. Identify specific point of disagreement
3. Escalate to human maintainer if needed
4. Document decision in `.github/docs/decision-matrices.md` for future reference

## References

- `.github/docs/decision-matrices.md` — Quick decisions
- `.github/docs/agent-workflows.md` — Practical examples
- `.github/specs/agents.md` — Agent file conventions
- `.github/specs/repository.md` — Repository design principles

---

**Version**: 2.0 - Adapted to BusinessInfinity (removed Genesis protocols)  
**Last Updated**: 2026-03-07  
**Purpose**: Define clear communication protocols for agent ecosystem
