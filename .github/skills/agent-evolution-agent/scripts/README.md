# Agent Evolution Scripts

**Purpose**: Automated validation and improvement tools for the agent intelligence system.

## Scripts Overview

### Quality Measurement

#### `audit-agent-quality.sh`
Analyzes all agents for quality metrics.

**Usage:**
```bash
./.github/skills/agent-evolution-agent/scripts/audit-agent-quality.sh
```

**Outputs:**
- Agent line counts vs targets
- Spec reference counts
- Spec coverage percentages
- Optimal vs needs improvement status
- Overall system metrics

---

#### `measure-context-efficiency.sh`
Deep analysis of a single agent's context window usage.

**Usage:**
```bash
./.github/skills/agent-evolution-agent/scripts/measure-context-efficiency.sh <agent-file>
```

**Example:**
```bash
./measure-context-efficiency.sh .github/instructions/python.instructions.md
```

**Outputs:**
- Size metrics (lines, characters, estimated tokens)
- Content structure (headers, lists, code blocks)
- Reference metrics (spec refs, doc refs)
- Efficiency score (0-100)
- Specific recommendations

---

### Intelligence & Detection

#### `detect-duplication.sh`
Finds duplicate content blocks across agents.

**Usage:**
```bash
./.github/skills/agent-evolution-agent/scripts/detect-duplication.sh
```

**How it works:**
1. Extracts content blocks from all agents
2. Creates normalized fingerprints
3. Detects duplicates across different agents
4. Reports sources and targets

**Dogfooding principle applied:**
- Code agents enforce clean separation of concerns
- Agent system enforces zero-duplication in prompts

---

#### `recommend-improvements.sh`
Generates actionable improvement recommendations.

**Usage:**
```bash
./.github/skills/agent-evolution-agent/scripts/recommend-improvements.sh
```

**Outputs:**
- Priority-ranked agents (high/medium/low)
- Specific recommendations for each agent
- Dogfooding principles to apply
- Next steps

**Recommendations include:**
- Lines to extract to specs
- Spec references to add
- Large code examples to move
- Extensive lists to consolidate

---

### Continuous Learning

#### `track-metrics.sh`
Records and tracks quality metrics over time.

**Usage:**
```bash
# Record current metrics
./.github/skills/agent-evolution-agent/scripts/track-metrics.sh

# View historical trends
./.github/skills/agent-evolution-agent/scripts/track-metrics.sh --history
```

**Tracks:**
- Total agents
- Optimal agents count/percentage
- Average spec coverage
- Average lines per agent
- Context efficiency score
- Total spec references

**Shows trends:**
- ↑ Green: Improvements since last run
- → Blue: No change
- ↓ Red: Regressions (requires attention)

**Data stored in:**
`.github/metrics/history.log`

---

### Synchronization

#### `find-related-agents.sh`
Identifies agents that should reference a given spec.

**Usage:**
```bash
./.github/skills/agent-evolution-agent/scripts/find-related-agents.sh <spec-file>
```

**Example:**
```bash
./find-related-agents.sh .github/specs/workflows.md
```

**How it works:**
1. Extracts keywords from spec filename
2. Checks agent files for keyword matches
3. Identifies agents already referencing spec ✓
4. Identifies agents that should reference spec

---

#### `sync-agents-with-specs.sh`
Checks if agents properly reference relevant specs.

**Usage:**
```bash
./.github/skills/agent-evolution-agent/scripts/sync-agents-with-specs.sh
```

**Detects:**
- Agents mentioning topics without spec references
- Missing coverage
- Sync issues to address

## Common Workflows

### Weekly Quality Check
```bash
cd .github/skills/agent-evolution-agent/scripts

# Baseline
./audit-agent-quality.sh
./track-metrics.sh
./detect-duplication.sh
./recommend-improvements.sh

# Review output and make improvements

# Verification
./audit-agent-quality.sh
./track-metrics.sh --history
```

### New Spec Added
```bash
cd .github/skills/agent-evolution-agent/scripts

# Find related agents
./find-related-agents.sh docs/specifications/new-spec.md

# For each related agent:
#   1. Add spec reference
#   2. Remove duplicated content
#   3. Verify improvement

# Sync check
./sync-agents-with-specs.sh
```

### Agent Improvement
```bash
cd .github/skills/agent-evolution-agent/scripts

# Analyze specific agent
./measure-context-efficiency.sh .github/prompts/my-agent.prompt.md

# Get recommendations
./recommend-improvements.sh | grep -A 20 "my-agent"

# Make improvements

# Verify
./measure-context-efficiency.sh .github/prompts/my-agent.prompt.md
./audit-agent-quality.sh
```

## Exit Codes

All scripts use standard exit codes:
- `0`: Success / No issues
- `1`: Issues found / Improvements needed

**Note**: Non-zero exit doesn't mean failure - it means action items detected.

## Target Metrics

Scripts enforce these quality standards:

| Metric | Target | Script |
|--------|--------|--------|
| Instruction files | ≤200 lines | audit, measure |
| Prompt files | ≤400 lines | audit, measure |
| Skill files | ≤150 lines | audit, measure |
| Spec references | ≥3 per agent | audit, recommend |
| Spec coverage | ≥80% average | audit, track |
| Duplication | 0 instances | detect |
| Context efficiency | ≥75/100 | measure, track |

## Integration

### Manual Use
Run scripts from any directory - they find paths automatically.

### Git Hooks
Add to `.git/hooks/pre-commit`:
```bash
#!/bin/bash
./.github/skills/agent-evolution-agent/scripts/detect-duplication.sh
```

### CI/CD
Add to workflow:
```yaml
- name: Agent Quality Check
  run: |
    ./.github/skills/agent-evolution-agent/scripts/audit-agent-quality.sh
    ./.github/skills/agent-evolution-agent/scripts/detect-duplication.sh
```

### Cron Job
Weekly automated tracking:
```bash
# crontab -e
0 9 * * 1 cd /path/to/repo && ./.github/skills/agent-evolution-agent/scripts/track-metrics.sh
```

## Troubleshooting

### "File not found" errors
Ensure you're running from repository root or use absolute paths.

### Permission denied
Make scripts executable:
```bash
chmod +x .github/skills/agent-evolution-agent/scripts/*.sh
```

### Unexpected metrics
- Clear metrics history: `rm .github/metrics/history.log`
- Re-establish baseline: `./track-metrics.sh`

## Related Documentation

- `.github/docs/dogfooding-guide.md` - Complete dogfooding guide
- `.github/skills/agent-evolution-agent/SKILL.md` - Meta-agent skill definition
- `/docs/specifications/agent-self-learning-system.md` - Technical architecture
- `/docs/specifications/github-copilot-agent-guidelines.md` - Agent standards

---

**Version**: 1.0  
**Last Updated**: 2026-02-10  
**Maintained by**: agent-evolution-agent (meta-intelligence)
