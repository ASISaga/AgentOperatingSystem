# Agent Intelligence Philosophy

**Last Updated**: 2026-03-07  
**Audience**: Agent developers, contributors

## Vision: Living Intelligence Architecture

This repository operates as a **living intelligence system** — not a static codebase, but an evolving ecosystem where AI agents act as:

- **Architecture Guardians** - Maintaining the lean, SDK-delegated structure
- **Evolution Facilitators** - Managing growth through PRs
- **Knowledge Curators** - Documenting the "why" behind every change
- **Quality Guardians** - Ensuring correctness and best practices
- **Self-Learning Optimizers** - Continuously improving the agent system itself

## Dogfooding Principle

**Agents use the same standards they enforce**:

- Code agents enforce clean separation of concerns → Agent files enforce zero-duplication
- Python agents enforce type hints and docstrings → Agent prompts have semantic role definitions
- Docs agents enforce spec references → Agents maximally reference `.github/specs/`

**Result**: The agent system **practices what it preaches**, creating a self-improving intelligence loop.

## Core Principles

### 1. Tool Leverage

Orchestrate existing automation, never duplicate. Reference repository documents, validation scripts, and test commands rather than reimplementing logic.

**Examples**:
- Use `pytest tests/ -v` rather than describing test commands
- Reference `.github/specs/` rather than duplicating technical details
- Invoke validation scripts rather than manually checking

### 2. Path Specificity

Instructions auto-load based on file patterns. Detailed coding standards live in `.github/instructions/` with `applyTo` glob patterns, keeping copilot-instructions.md concise.

**Benefits**:
- Context-appropriate guidance
- No overwhelming agents with irrelevant details
- Easier maintenance and updates

### 3. Context Efficiency

Reference specs/docs, eliminate redundancy. Maximize useful information within GitHub Copilot's context window by pointing to detailed documentation rather than duplicating it.

**Metrics**:
- Spec coverage: Percentage of agents with proper references
- Context efficiency: Information density per token
- Duplication rate: Repeated content across files

### 4. Ouroboros Pattern

Agents evolve themselves through continuous use. The agent-evolution-agent uses its own principles to improve the agent ecosystem, creating a recursive improvement loop.

**Self-Learning Loop**:
```
Codebase Change → Spec Update → Agent Sync → Refactor → Validate → Metrics → Improve
```

## Agent Intelligence Architecture

**Five-pillar structure**:

1. **Instructions** (`.github/instructions/`) - Path-activated coding standards
2. **Specifications** (`.github/specs/`) - Detailed technical frameworks
3. **Documentation** (`.github/docs/`) - Implementation guides and references
4. **Agents** (`.github/agents/`, `.github/prompts/`) - Executable intelligence
5. **Skills** (`.github/skills/`) - Reusable capabilities

Each pillar has a specific purpose and cross-references the others to maintain coherence without duplication.

## Separation of Concerns

At the heart of this repository is a clear **separation of concerns** — business logic here, infrastructure in the SDK.

**Agents must**:
- Keep workflow functions focused on business orchestration only
- Delegate infrastructure concerns to `aos-client-sdk`
- Document intent (purpose, purpose_scope) not implementation

**Example transformations**:
- ❌ "Add Azure Functions boilerplate" → ✅ "Use `app.get_functions()`"
- ❌ "Manage Service Bus manually" → ✅ "SDK handles messaging"
- ❌ "Implement agent logic" → ✅ "Declare purpose and let AOS orchestrate"

## Evolution Over Perfection

The system should grow organically based on real needs:

- Accept imperfection as starting point
- Document every evolution with reasoning
- Allow old decisions to be revisited
- Prioritize patterns used by multiple contexts
- Refactor when complexity outweighs clarity

## Quality Indicators

**Healthy system**:
- 📈 Agents reference specs consistently
- 📈 Low duplication across files
- 📈 High context efficiency
- 📈 Clear separation of concerns
- 📈 Self-improvement metrics trending positive

**Unhealthy patterns**:
- 📉 Agents duplicating spec content
- 📉 Copilot-instructions.md growing beyond 200 lines
- 📉 Missing or broken cross-references
- 📉 Agents unable to find relevant information
- 📉 Metrics stagnating or declining

## Active Implementation

**Dogfooding is automated** - not just philosophy:

### Validation Scripts

```bash
./.github/skills/agent-evolution-agent/scripts/audit-agent-quality.sh    # Quality audit
./.github/skills/agent-evolution-agent/scripts/detect-duplication.sh     # Duplication check
./.github/skills/agent-evolution-agent/scripts/recommend-improvements.sh # Recommendations
./.github/skills/agent-evolution-agent/scripts/track-metrics.sh          # Track trends
```

### Metrics Tracking

`.github/metrics/` stores historical data tracking agent quality over time.

**Goal**: Ouroboros loop — agents continuously improving agents

## References

**Related Documentation**:
- `.github/specs/repository.md` - Repository-specific spec
- `.github/specs/agent-intelligence-framework.md` - Complete framework specification
- `.github/docs/dogfooding-guide.md` - Self-improvement workflows
- `.github/docs/agent-metrics.md` - Measuring system health
- `.github/docs/conventional-tools.md` - All validation commands

---

**Version**: 2.1 - Made repository-agnostic  
**Last Updated**: 2026-03-07  
**Purpose**: Define philosophical foundation for agent intelligence system
