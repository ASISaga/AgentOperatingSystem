# Agent Metrics & System Health

**Last Updated**: 2026-02-14  
**Audience**: Agent developers, system maintainers

## Overview

Metrics for measuring agent ecosystem health and tracking continuous improvement.

## Core Metrics

| Metric | Target | Command |
|--------|--------|---------|
| **Spec Coverage** — % of agent files referencing specs | ≥80% | `./check-spec-coverage.sh` |
| **Context Efficiency** — Info density per token | ≥50 | `./measure-context-efficiency.sh` |
| **Duplication Score** — % content repeated across files | <10% | `./detect-duplication.sh` |
| **Validation Pass Rate** — % files passing quality checks | ≥90% | `./validate-all-agents.sh` |
| **Optimal Agent %** — % agents meeting all criteria | ≥25% | `./quick-health-check.sh` |

All scripts located in: `.github/skills/agent-evolution-agent/scripts/`

### Optimal Agent Criteria

Spec coverage >80%, context efficiency >50, file size <200 lines, clear references, no duplication, all validations pass.

## Health Indicators

**Healthy**: Agent files getting smaller, spec files getting richer, doc files current (<30 days), broken references absent, duplication absent.

**Unhealthy**: Duplicate content accumulating, broken references growing, spec coverage declining, agent files growing in size.

## Quarterly Review

### Documentation Manager Agent
- [ ] Run structure validation: `./.github/skills/documentation-manager-agent/scripts/validate-doc-structure.sh`
- [ ] Check for redundancy: `./.github/skills/documentation-manager-agent/scripts/detect-doc-redundancy.sh`
- [ ] Verify metadata: `./.github/skills/documentation-manager-agent/scripts/check-doc-metadata.sh`

### Agent Evolution Agent
- [ ] Run full audit: `./audit-agent-quality.sh`
- [ ] Compare trends to last quarter
- [ ] Extract repeated content to specs, fix broken references
- [ ] Self-check: Is agent-evolution-agent itself optimal?

## Measurement Commands

```bash
# Quick health check (all metrics)
cd .github/skills/agent-evolution-agent/scripts
./audit-agent-quality.sh

# Track metrics over time
./track-metrics.sh

# Historical comparison
./track-metrics.sh --history
```

## Improvement Workflows

- **Spec coverage <80%**: Run `./find-agents-without-specs.sh`, add spec references, remove duplicated content
- **Context efficiency <50**: Run `./detect-duplication.sh`, extract to specs/docs, replace with references
- **Validation <90%**: Run `./validate-all-agents.sh --verbose`, fix YAML fields, broken references, formatting

## References

- `.github/docs/dogfooding-guide.md` — Self-improvement workflows
- `.github/skills/agent-evolution-agent/SKILL.md` — Validation tools
- `.github/specs/agents.md` — Agent file specification
- `.github/specs/skills.md` — Skill file specification
- `.github/specs/agent-intelligence-framework.md` — Framework spec

---

**Version**: 2.0 - Adapted to BusinessInfinity  
**Last Updated**: 2026-03-07  
**Purpose**: Define and track agent ecosystem quality metrics
