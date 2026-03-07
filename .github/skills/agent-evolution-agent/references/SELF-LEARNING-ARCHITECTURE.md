# Agent Self-Learning Architecture

**Version**: 2.0  
**Last Updated**: 2026-03-07  
**Status**: Active

This document describes the dogfooding-based self-learning architecture that enables the agent intelligence system to continuously evolve.

## Philosophy

The agent ecosystem implements **dogfooding** — agents use the same principles they enforce to improve themselves:

| Principle | Applied to Code | Applied to Agents |
|-----------|----------------|-------------------|
| **Zero Duplication** | Code: No repeated logic across modules | Agents: No duplicate knowledge across files |
| **Semantic Structure** | Code: Meaningful names and clear organization | Agents: Clear role definitions and scope |
| **Spec References** | Code: Reference authoritative specs | Agents: Reference `.github/specs/` |
| **Lean Context** | Files: Minimal line count, high signal | Agents: Optimized token usage |

## Self-Learning Loop

```
┌──────────────────────────────────────────────────────────────┐
│                     Continuous Evolution                      │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Codebase Change │
                    │  (New Pattern)   │
                    └────────┬─────────┘
                             │
                             ▼
                   ┌──────────────────┐
                   │ Pattern Detection│ ← Git hooks, CI/CD
                   │   (Automated)    │
                   └────────┬─────────┘
                            │
                            ▼
                  ┌──────────────────────┐
                  │ Specification Update │ ← Human or Agent
                  │   /docs/specs/       │
                  └────────┬─────────────┘
                           │
                           ▼
                ┌──────────────────────────┐
                │ Agent Sync Check         │ ← sync-agents-with-specs.sh
                │ (Find related agents)    │
                └────────┬─────────────────┘
                         │
                         ▼
              ┌───────────────────────────┐
              │ Agent Refactor            │ ← agent-evolution-agent
              │ (Add spec references)     │
              └────────┬──────────────────┘
                       │
                       ▼
            ┌──────────────────────────┐
            │ Quality Validation       │ ← audit-agent-quality.sh
            │ (Measure effectiveness)  │
            └────────┬─────────────────┘
                     │
                     ▼
           ┌──────────────────────┐
           │ Metrics Tracking     │ ← Store in memory/logs
           │ (Learn & Improve)    │
           └──────────────────────┘
```

## Learning Mechanisms

### 1. Pattern Detection

**Trigger**: Repeated code patterns in commits

**Mechanism**:
```bash
# Git hooks detect patterns
git log --all --pretty=format:'' --name-only | sort | uniq -c | sort -rn

# If pattern count > threshold, flag for documentation
```

**Example**:
- 5 commits add a new workflow pattern → Update workflows spec
- 3 files share the same orchestration boilerplate → Add to patterns spec

### 2. Specification Sync

**Trigger**: New file in `.github/specs/`

**Mechanism**:
```bash
# On spec file change
git diff --name-only HEAD~1 .github/specs/

# Find related agents
./scripts/find-related-agents.sh $spec_file

# Suggest updates to agents
```

**Output**: PR suggestion with spec references to add

### 3. Context Optimization

**Trigger**: Weekly audit or agent file size increase

**Mechanism**:
```bash
# Measure all agents
./scripts/audit-agent-quality.sh

# Identify verbose agents
# Extract knowledge to specs
# Replace with references
```

**Metrics**:
- Before: 450 lines, 2 spec refs, 44% efficiency
- After: 280 lines, 5 spec refs, 82% efficiency

### 4. Quality Feedback

**Trigger**: Agent validation failures

**Mechanism**:
- Track validation script pass/fail rates
- Identify common failure patterns
- Update agent instructions to prevent
- Document in specs

**Example**:
- `validate-spec.sh` fails on missing acceptance criteria → Update spec-manager instructions
- Pattern repeated 3x → Create spec section on common mistakes

## Metrics & Monitoring

### Key Performance Indicators

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Spec Coverage** | ≥80% | % of knowledge in specs vs agents |
| **Context Efficiency** | ≥75 score | Lines, refs, token usage combined |
| **Duplication Ratio** | ≤10% | Repeated content across agents |
| **Validation Pass Rate** | ≥95% | Script success percentage |
| **Spec References** | ≥3 per agent | Count of `.github/specs/` links |

### Dashboard (Conceptual)

```
Agent Ecosystem Health

Spec Coverage:        ████████░░ 82% ✓
Context Efficiency:   ███████░░░ 74  ⚠
Duplication Ratio:    ██░░░░░░░░ 8%  ✓
Validation Pass Rate: █████████░ 92% ✓

Agents Needing Attention:
  • documentation-manager-agent (verbose, 450 lines)
  • spec-manager (low spec refs, 2)

Recent Improvements:
  • agent-evolution-agent: +3 spec refs
  • python.instructions: -120 lines
```

## Evolution Triggers

### Automatic Triggers

1. **Spec File Added** → Run `find-related-agents.sh`
2. **Agent File Size >400 Lines** → Flag for optimization
3. **Validation Failure Rate >10%** → Review agent instructions
4. **Duplicate Content Detected** → Consolidation suggestion

### Manual Triggers

1. **Weekly Quality Review** → Run `audit-agent-quality.sh`
2. **Major Codebase Change** → Update related specs
3. **New Pattern Discovered** → Document in `.github/specs/`
4. **Agent Feedback** → Incorporate learnings

## Best Practices

### For Agent Developers

1. **Always reference specs first**
   ```markdown
   → Complete guide: .github/specs/workflows.md
   ```

2. **Extract, don't duplicate**
   - Static knowledge → `.github/specs/`
   - Activation logic → Agent prompts
   - Workflows → Agent skills

3. **Measure before committing**
   ```bash
   ./scripts/measure-context-efficiency.sh .github/prompts/my-agent.prompt.md
   ```

4. **Version your changes**
   ```markdown
   **Version History**:
   - v1.1 (2026-03-07): Added spec references, reduced 150 lines
   ```

### For Spec Writers

1. **Make specs discoverable**
   - Clear filenames with keywords
   - Rich introductions
   - Cross-references to related specs

2. **Structure for reference**
   - Quick start sections
   - Detailed examples
   - Decision matrices
   - Common patterns

3. **Update agents when specs change**
   ```bash
   # After updating spec
   ./scripts/find-related-agents.sh .github/specs/my-spec.md
   ```

## Integration Points

### With Existing Systems

| System | Integration |
|--------|-------------|
| **Git** | Hooks detect pattern changes |
| **CI/CD** | Runs quality audits on PR |
| **pytest** | Validation scripts in test suite |
| **GitHub Actions** | Auto-generates improvement PRs |
| **Copilot** | Uses evolved agents for better suggestions |

### With Future Systems

| System | Planned Integration |
|--------|---------------------|
| **Analytics** | Track agent usage patterns |
| **A/B Testing** | Compare agent effectiveness |
| **ML Pipeline** | Learn from successful agents |
| **Auto-Documentation** | Generate specs from code patterns |

## Security & Safety

### Safeguards

1. **Human Review Required**
   - Automated PRs need approval
   - Metrics inform, don't decide
   - Agent changes versioned

2. **Validation Gates**
   - All script changes tested
   - Agent syntax validated
   - Cross-reference integrity checked

3. **Rollback Capability**
   - Git history preserves all versions
   - Specs and agents versioned together
   - Breaking changes documented

## Future Enhancements

### Phase 2 (Planned)

1. **ML-Based Pattern Detection**
   - Train on commit patterns
   - Predict spec needs
   - Suggest agent improvements

2. **Real-Time Monitoring**
   - Live agent effectiveness dashboard
   - Alert on quality degradation
   - Auto-trigger optimization

3. **Cross-Repository Learning**
   - Share agent improvements across subdomains
   - Federated learning from all repos
   - Universal pattern library

4. **Predictive Evolution**
   - Anticipate codebase needs
   - Pre-emptive spec creation
   - Proactive agent adaptation

---

**References**:
- Agent Evolution Skill: `.github/skills/agent-evolution-agent/SKILL.md`
- Dogfooding Guide: `.github/docs/dogfooding-guide.md`
- Agent Philosophy: `.github/docs/agent-philosophy.md`
- Agent Spec: `.github/specs/agents.md`
- Skill Spec: `.github/specs/skills.md`
