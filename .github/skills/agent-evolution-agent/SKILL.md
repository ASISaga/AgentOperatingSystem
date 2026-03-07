---
name: agent-evolution-agent
description: Meta-agent that evolves the agent intelligence system through dogfooding, continuous learning, and specification-driven optimization for maximum context window efficiency
license: MIT
metadata:
  author: ASISaga
  version: "1.2"
  category: meta-intelligence
  role: self-evolution-specialist
allowed-tools: Bash(npm:*) Bash(git:*) Read Edit
---

# Agent Evolution Agent

**Role**: Meta-Intelligence Self-Evolution Specialist  
**Scope**: `.github/` agent ecosystem  
**Version**: 1.2 - High-Density Refactor

## Purpose

Meta-agent implementing **dogfooding principle**: agents improve agents using same standards they enforce. Optimizes context window usage and maximizes spec leverage.

## When to Use This Skill

Activate when:
- New specs added to `.github/specs/`
- Agent prompts become outdated/verbose
- Duplicate knowledge across agents/specs
- Context window efficiency needs improvement
- Agent quality metrics show issues

## Core Principles

**Dogfooding**: Agents improve agents  
- Code agents → clean separation | Agent prompts → zero-duplication  
- Domain agents → semantic | Agent structure → semantic  
- Docs agents → spec refs | Agent prompts → spec refs

**Spec-Driven**: Detailed knowledge in specs, not prompts  
**Continuous**: Auto-adapt to codebase changes  
**Measurable**: Track quality metrics

→ **Complete architecture**: `.github/docs/dogfooding-guide.md`

## Quick Workflows

### 1. Quality Audit

```bash
./.github/skills/agent-evolution-agent/scripts/audit-agent-quality.sh

# Shows: optimal vs needs improvement, spec coverage, context efficiency
```

### 2. Spec Sync Check

```bash
./.github/skills/agent-evolution-agent/scripts/find-related-agents.sh <spec-file>

# Shows: agents that should reference the spec
```

### 3. Duplication Detection

```bash
./.github/skills/agent-evolution-agent/scripts/detect-duplication.sh

# Shows: duplicate content across agents
```

### 4. Improvement Recommendations

```bash
./.github/skills/agent-evolution-agent/scripts/recommend-improvements.sh

# Shows: priority-ranked improvement actions
```

### 5. Metrics Tracking

```bash
./.github/skills/agent-evolution-agent/scripts/track-metrics.sh [--history]

# Shows: quality trends over time
```

→ **All scripts**: `scripts/README.md`

## Target Metrics

**Instruction files**: ≤200 lines  
**Prompt files**: ≤400 lines  
**Skill files**: ≤150 lines  
**Spec references**: ≥3 per agent  
**Spec coverage**: ≥80% average

## Validation

**Before committing agent changes:**

```bash
# Quality audit
./scripts/audit-agent-quality.sh

# Check duplication
./scripts/detect-duplication.sh

# Test functionality
npm test
```

## Resources

**Spec Files**:
- `.github/specs/agents.md` - Agent file specification
- `.github/specs/skills.md` - Skill file specification
- `.github/specs/prompts.md` - Prompt file specification
- `.github/specs/instructions.md` - Instruction file specification

**Documentation**:
- `scripts/README.md` - **All validation scripts**
- `references/SELF-LEARNING-ARCHITECTURE.md` - Detailed architecture
- `.github/docs/dogfooding-guide.md` - Dogfooding workflows
- `.github/docs/agent-philosophy.md` - Ecosystem architecture
- `.github/docs/agent-system-overview.md` - Agent catalog and navigation

**Related Skills**: documentation-manager-agent, spec-manager

---

**Version History**:
- **v1.2** (2026-02-10): High-density refactor - 229→137 lines, enhanced spec references
- **v1.1** (2026-02-10): Added duplication, recommendations, metrics tracking
- **v1.0**: Initial meta-agent implementation
