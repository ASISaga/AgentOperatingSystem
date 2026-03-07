# Agent System Overview

**Last Updated**: 2026-03-07

Overview of the GitHub Copilot agent intelligence system: directory structure, agent catalog, and learning paths.

---

## Directory Structure

```
.github/
├── copilot-instructions.md          # High-level architecture context
├── instructions/                    # Path-activated coding standards (glob-based)
│   ├── python.instructions.md       #   Python coding standards (PEP 8, async, type hints)
│   ├── azure-functions.instructions.md  #   Azure Functions / AOS workflow patterns
│   ├── docs.instructions.md         #   Documentation standards
│   ├── agents.instructions.md       #   Agent file standards
│   ├── prompts.instructions.md      #   Prompt file standards
│   └── skills.instructions.md       #   Skill file standards
├── specs/                           # Detailed specifications & frameworks
│   ├── repository.md                    # Repository-specific spec (update per repo)
│   └── agent-intelligence-framework.md  # Generic agent system framework
├── docs/                            # Documentation & guides (this directory)
├── agents/                          # Custom agents (*.agent.md)
├── prompts/                         # Agent prompts (*.prompt.md)
└── skills/                          # Agent skills (SKILL.md + scripts)
    └── {agent-name}/
        ├── SKILL.md
        ├── scripts/                 #   Validation & automation
        └── references/              #   Detailed specifications
```

**Key principle**: Instructions auto-load via `applyTo` glob patterns. Specs and docs are referenced, never duplicated.

---

## Agent Catalog

### Meta-Intelligence

| Agent | Skill | Purpose |
|-------|-------|---------|
| Agent Evolution | `.github/skills/agent-evolution-agent/` | Audits and improves the agent ecosystem (Ouroboros) |

### Support

| Agent | Skill | Purpose |
|-------|-------|---------|
| Documentation Manager | `.github/skills/documentation-manager-agent/` | Validates documentation structure, links, and metadata |
| Repository Onboarding | `.github/skills/repository-onboarding/` | Bootstraps agent intelligence in new repositories |

All prompts are in `.github/prompts/`. Validation scripts are under `.github/skills/{agent}/scripts/`.

---

## Agent Evolution Agent

The meta-intelligence agent audits and improves the agent ecosystem itself.

**Scripts** (in `.github/skills/agent-evolution-agent/scripts/`):

| Script | Purpose |
|--------|---------|
| `audit-agent-quality.sh` | Quality metrics audit |
| `find-related-agents.sh` | Find agents for a spec |
| `measure-context-efficiency.sh` | Context window analysis |
| `sync-agents-with-specs.sh` | Spec synchronization |
| `detect-duplication.sh` | Cross-agent duplication detection |
| `recommend-improvements.sh` | Improvement recommendations |
| `track-metrics.sh` | Quality metrics over time |

---

## Path-Activated Instructions

Each instruction file has an `applyTo` glob pattern in its YAML frontmatter:

```yaml
---
applyTo: "**/*.py"
description: "Python coding standards"
---
```

When editing a matching file, GitHub Copilot automatically loads the relevant instructions.

**Context loading order**:
```
copilot-instructions.md  →  .github/instructions/  →  .github/specs/
(high-level context)        (path-specific details)    (complete references)
```

Detailed guide: `.github/docs/path-specific-instructions.md`

---

## Common Workflows

### Adding a new workflow

```python
# 1. Add @app.workflow decorator in src/<package>/workflows.py
@app.workflow("new-workflow")
async def new_workflow(request: WorkflowRequest) -> Dict[str, Any]:
    ...

# 2. Run tests
pytest tests/ -v

# 3. Update test_workflow_count if needed
```

### Validating Python code

```bash
pytest tests/ -v                        # Run all tests
pylint src/                             # Lint
```

### Agent Quality (Dogfooding)

```bash
./.github/skills/agent-evolution-agent/scripts/audit-agent-quality.sh
./.github/skills/agent-evolution-agent/scripts/detect-duplication.sh
./.github/skills/agent-evolution-agent/scripts/recommend-improvements.sh
```

### Documentation Quality

```bash
./.github/skills/documentation-manager-agent/scripts/validate-doc-structure.sh
./.github/skills/documentation-manager-agent/scripts/validate-doc-links.sh docs/
./.github/skills/documentation-manager-agent/scripts/detect-doc-redundancy.sh
./.github/skills/documentation-manager-agent/scripts/check-doc-metadata.sh docs/specifications/
```

---

## Learning Paths

### New Contributors

1. Read `README.md` — project overview and architecture
2. Read `.github/specs/repository.md` — repository-specific spec
3. Read `agent-philosophy.md` — core principles
4. Run `pytest tests/ -v` — verify your setup

### AI Agents

1. Load `.github/specs/repository.md` for project context
2. Load `.github/instructions/python.instructions.md` when editing Python
3. Load `.github/instructions/azure-functions.instructions.md` when editing workflows
4. Run `pytest tests/ -v` to validate output

### Repository Maintainers

1. Run `pytest tests/ -v` before merging
2. Run agent evolution scripts for agent quality
3. Keep `repository.md` spec current

---

## Key Resources

| Resource | Location |
|----------|----------|
| Repository Spec | `.github/specs/repository.md` |
| Python Standards | `.github/instructions/python.instructions.md` |
| Azure Functions Patterns | `.github/instructions/azure-functions.instructions.md` |
| Agent Framework Spec | `.github/specs/agent-intelligence-framework.md` |
| Agent Philosophy | `.github/docs/agent-philosophy.md` |
| Conventional Tools | `.github/docs/conventional-tools.md` |
| Dogfooding Guide | `.github/docs/dogfooding-guide.md` |
