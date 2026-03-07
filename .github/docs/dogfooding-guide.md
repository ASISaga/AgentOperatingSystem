# Agent Dogfooding Guide

**Version**: 2.0  
**Last Updated**: 2026-03-07  
**Status**: Production Active

## Overview

This guide explains how the GitHub Copilot agent system practices **dogfooding** — using the same principles it enforces on code to continuously improve itself. The guide is actionable: every workflow maps to a real agent, script, or file in `.github/`.

## What is Dogfooding?

**Dogfooding** (eating your own dog food) means agents use the same standards they enforce:

| What Agents Enforce on Code | How Agents Apply to Themselves |
|------------------------------|--------------------------------|
| **Clean separation of concerns** | Zero-duplication in agent prompts |
| **Semantic role definitions** | Clear scope per agent/prompt/skill |
| **Spec references in code** | Maximum spec references in agents |
| **Lean context usage** | Optimized token usage in prompts |
| **Validation scripts** | Automated agent quality audits |

## Self-Learning Loop

```
┌─────────────────────────────────────────────────────────┐
│                 Continuous Learning Cycle                │
└─────────────────────────────────────────────────────────┘
                            │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   Measure    │   │   Improve    │   │   Validate   │
│   Metrics    │──▶│    Agents    │──▶│   Quality    │
└──────────────┘   └──────────────┘   └──────────────┘
        ▲                                      │
        │                                      │
        └──────────────────────────────────────┘
                    Track Progress
```

## Validation Scripts

### 1. Quality Audit
**Purpose**: Measure all agent quality metrics

```bash
./.github/skills/agent-evolution-agent/scripts/audit-agent-quality.sh
```

**Output:**
- Total agents analyzed
- Optimal vs needs improvement
- Average spec coverage
- Specific agent status

**Target Metrics:**
- Instruction files: ≤200 lines
- Prompt files: ≤400 lines
- Skill files: ≤150 lines
- Spec references: ≥3 per agent
- Spec coverage: ≥80% average

### 2. Context Efficiency
**Purpose**: Analyze context window usage for a specific agent

```bash
./.github/skills/agent-evolution-agent/scripts/measure-context-efficiency.sh <agent-file>
```

**Example:**
```bash
./scripts/measure-context-efficiency.sh .github/instructions/python.instructions.md
```

**Scores:**
- 80-100: Excellent (highly optimized)
- 60-79: Good (well-optimized)
- 40-59: Needs improvement
- 0-39: Poor (requires refactoring)

### 3. Duplication Detection
**Purpose**: Find duplicate content across agents

```bash
./.github/skills/agent-evolution-agent/scripts/detect-duplication.sh
```

**Applies dogfooding:**
- Code agents enforce clean separation of concerns
- Agent system enforces zero-duplication

**Action if duplicates found:**
1. Extract shared content to `.github/specs/` (preferred) or `/docs/specifications/`
2. Replace duplicates with spec references
3. Re-run to verify

### 4. Improvement Recommendations
**Purpose**: Generate actionable improvement steps

```bash
./.github/skills/agent-evolution-agent/scripts/recommend-improvements.sh
```

**Output:**
- Priority-ranked agents needing improvement
- Specific recommendations for each
- Dogfooding principles to apply
- Next steps

### 5. Metrics Tracking
**Purpose**: Track quality metrics over time

```bash
# Record current metrics
./.github/skills/agent-evolution-agent/scripts/track-metrics.sh

# View historical trends
./.github/skills/agent-evolution-agent/scripts/track-metrics.sh --history
```

**Tracks:**
- Total agents
- Optimal agents (%)
- Spec coverage (%)
- Context efficiency score
- Total spec references

**Shows trends:**
- ↑ Green: Improvements
- → Blue: No change
- ↓ Red: Regressions

### 6. Related Agent Finder
**Purpose**: Find agents that should reference a spec

```bash
./.github/skills/agent-evolution-agent/scripts/find-related-agents.sh <spec-file>
```

**Example:**
```bash
./scripts/find-related-agents.sh .github/specs/workflows.md
```

**Output:**
- Agents already referencing the spec ✓
- Agents that should reference it (by keyword match)
- Recommended action

### 7. Spec Synchronization
**Purpose**: Check if agents reference relevant specs

```bash
./.github/skills/agent-evolution-agent/scripts/sync-agents-with-specs.sh
```

**Detects:**
- Agents mentioning topics without referencing specs
- Missing spec coverage
- Sync issues to address

## Weekly Quality Workflow

### Monday: Baseline Measurement
```bash
# 1. Audit current quality
./.github/skills/agent-evolution-agent/scripts/audit-agent-quality.sh

# 2. Record metrics
./.github/skills/agent-evolution-agent/scripts/track-metrics.sh

# 3. Check for duplicates
./.github/skills/agent-evolution-agent/scripts/detect-duplication.sh

# 4. Get recommendations
./.github/skills/agent-evolution-agent/scripts/recommend-improvements.sh
```

### Tuesday-Thursday: Improvements
For each agent needing improvement:

1. **Extract knowledge to specs:**
   - Identify static content (examples, lists, tables)
   - Create/update relevant spec in `.github/specs/` (preferred) or `/docs/specifications/`
   - Move content from agent to spec

2. **Add spec references:**
   - Find related specs: `./scripts/find-related-agents.sh <spec>`
   - Add to agent's "Related Documentation" section
   - Format: `→ Complete guide: .github/specs/X.md`

3. **Validate:**
   ```bash
   pytest tests/ -v  # Ensure no breaking changes
   ./scripts/measure-context-efficiency.sh <agent>  # Verify improvement
   ```

### Friday: Verification
```bash
# 1. Re-audit
./.github/skills/agent-evolution-agent/scripts/audit-agent-quality.sh

# 2. Track improvements
./.github/skills/agent-evolution-agent/scripts/track-metrics.sh --history

# 3. Verify no duplicates
./.github/skills/agent-evolution-agent/scripts/detect-duplication.sh

# 4. Check sync
./.github/skills/agent-evolution-agent/scripts/sync-agents-with-specs.sh
```

## When Specs Are Updated

After adding/updating `.github/specs/` files:

```bash
# 1. Find related agents
./.github/skills/agent-evolution-agent/scripts/find-related-agents.sh .github/specs/<new-spec>.md

# 2. For each related agent:
#    - Add spec reference
#    - Remove any duplicated content
#    - Verify with context efficiency check

# 3. Sync check
./.github/skills/agent-evolution-agent/scripts/sync-agents-with-specs.sh
```

## Invoking the Agent Intelligence System

Dogfooding is implemented through specific agents and skills in `.github/`. Use them directly:

### Run the Agent Evolution Agent

```bash
# Invoke via GitHub Copilot (Chat or agent mode)
# Use skill: agent-evolution-agent
```

→ **Agent definition**: `.github/agents/agent-evolution-agent.agent.md`  
→ **Skill**: `.github/skills/agent-evolution-agent/SKILL.md`

### Update Specs (Spec Manager)

When you discover new patterns or update technical knowledge:

```bash
# Invoke via GitHub Copilot agent mode
# Use agent: spec-manager
```

→ **Agent**: `.github/agents/spec-manager.agent.md`  
→ **Prompts**: `.github/prompts/spec-create.prompt.md`, `spec-plan.prompt.md`, `spec-tasks.prompt.md`

### Validate Documentation (Documentation Manager)

After updating agents/specs:

```bash
# Invoke via GitHub Copilot agent mode
# Use agent: documentation-manager-agent
```

→ **Agent**: `.github/agents/documentation-manager-agent.agent.md`  
→ **Skill**: `.github/skills/documentation-manager-agent/SKILL.md`

## System Files Reference

| Category | Location | Purpose |
|----------|----------|---------|
| Agent definitions | `.github/agents/*.agent.md` | Entry points for agent execution |
| Prompt workflows | `.github/prompts/*.prompt.md` | Detailed task prompts |
| Skills | `.github/skills/*/SKILL.md` | Executable capabilities with scripts |
| Path instructions | `.github/instructions/*.instructions.md` | Auto-loaded coding standards |
| Specifications | `.github/specs/*.md` | Authoritative technical frameworks |
| Metrics history | `.github/metrics/` | Historical quality data |

## Best Practices

### 1. Spec References Over Duplication
❌ **Don't:**
```markdown
## Domain Pattern

The pattern has 3 variants:
- Variant 1: description...
- Variant 2: description...
[... 50 lines of pattern details ...]
```

✅ **Do:**
```markdown
## Domain Pattern

Use the pattern defined in the spec for all implementations.

→ **Complete patterns**: `.github/specs/workflows.md`
→ **Enterprise capabilities**: `.github/specs/enterprise-capabilities.md`
```

### 2. Minimal Examples Inline
❌ **Don't include 10+ code examples**

✅ **Do:**
- 1-2 minimal examples inline
- Reference spec for comprehensive examples
- Link to working samples in codebase

### 3. Progressive Refinement
- Start with baseline metrics
- Improve incrementally
- Track trends weekly
- Celebrate improvements

### 4. Apply Dogfooding Principles
For each agent type:
- **Workflow/domain agents**: Minimize inline implementation details, reference `.github/specs/workflows.md`
- **Docs agents**: Reference specs, don't duplicate; invoke `documentation-manager-agent`
- **Meta-intelligence agents**: Use validation scripts, track metrics; invoke `agent-evolution-agent`

## Success Metrics

### Target Goals
- **Spec Coverage**: ≥90% (currently: 86%)
- **Optimal Agents**: ≥80% (currently: 27%)
- **Context Efficiency**: ≥85 (currently: 56)
- **Duplication**: 0 instances
- **All agents**: ≥3 spec references

### Track Progress
```bash
# Monthly report
echo "=== Agent Quality Report $(date +%Y-%m) ==="
./.github/skills/agent-evolution-agent/scripts/audit-agent-quality.sh
echo ""
./.github/skills/agent-evolution-agent/scripts/track-metrics.sh --history
```

## Continuous Improvement

The agent system is designed to continuously improve:

1. **Measure**: Run audits to establish baseline
2. **Improve**: Apply recommendations incrementally
3. **Validate**: Check quality metrics
4. **Track**: Record progress over time
5. **Repeat**: Weekly cycle

**Goal**: The agent system becomes smarter by practicing what it preaches.

## Related Documentation

→ **Agent file spec**: `.github/specs/agents.md`  
→ **Skill file spec**: `.github/specs/skills.md`  
→ **Prompt file spec**: `.github/specs/prompts.md`  
→ **Instructions spec**: `.github/specs/instructions.md`  
→ **Agent philosophy**: `.github/docs/agent-philosophy.md`  
→ **Meta-agent skill**: `.github/skills/agent-evolution-agent/SKILL.md`  
→ **Agent system overview**: `.github/docs/agent-system-overview.md`

---

**Remember**: Dogfooding isn't just about metrics — it's about building a self-improving intelligence system that continuously evolves to become more effective.
