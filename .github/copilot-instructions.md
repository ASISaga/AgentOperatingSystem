# GitHub Copilot Agent Meta-Intelligence System

This repository uses a structured GitHub Copilot Coding agent meta-intelligence system for optimal AI-assisted development.

## Directory Structure

### Specifications for repository for spec driven development
.github/specs/repository.md         #   ← Repository-specific spec (update per repo), and may delegate to further specifications in this directory.

### Specifications for spec driven development (Adhering to GitHub recommended Templates)
.github/specs/agents.md             # Specifications for agent files in .github/agents directory 
.github/specs/prompts.md            # Specifications for prompt files in .github/prompts directory
.github/specs/skills.md             # Specifications for files in .github/skills directory
.github/specs/instructions.md       # Specifications for files in .github/instructions directory

# GitHub Copilot Coding Agent files
.github/copilot-instructions.md     # This file - high-level GitHub Copilot Agent Meta-Intelligence System architecture
.github/instructions/               # Path-specific GitHub Copilot Coding Agent custom intructions (auto-load by glob), for GitHub Copilot agent meta-intelligence system, as well as repository. They maintain lean structure, and mandatorily leaverage appropriate files in .github/specs.

.github/docs/                       # Implementation guides & references
.github/agents/                     # Copilot Custom agents (*.agent.md)
.github/prompts/                    # Copilot Agent prompts (*.prompt.md)
.github/skills/                     # Copilot Agent skills (SKILL.md + scripts) applicable to the meta-intelligence system, as well as repository-specific skills
.github/workflows/                  # GitHub Workflows

- **Instructions/Agents/Prompts/Skills** auto-loaded by GitHub Copilot Coding Agent during execution
- **Specs** Are lean-and-mean, and define frameworks; **Docs** provide guides. This distinction is to be mandatorily maintained.
- **Validation** via agent quality scripts ensures continuous quality

## References
→ **Framework**: `.github/docs/agent-intelligence-framework.md`  
→ **Philosophy**: `.github/docs/agent-philosophy.md`  
→ **System overview**: `.github/docs/agent-system-overview.md`  
→ **Documentation index**: `.github/docs/README.md`

## Core Principles

1. **Tool Leverage** — Orchestrate existing automation, never duplicate
2. **Path Specificity** — Instructions auto-load based on file patterns
3. **Context Efficiency** — Reference specs/docs, eliminate redundancy
4. **Ouroboros Pattern** — Agents evolve themselves through continuous use

## Tools & Validation

→ **Repository tools & commands**: `.github/specs/repository.md`  
→ **Complete tool reference**: `.github/docs/conventional-tools.md`  
→ **Dogfooding guide**: `.github/docs/dogfooding-guide.md`  
→ **CI/CD workflow**: `.github/workflows/ci.yml`

```bash
# Agent quality validation (repository-agnostic)
./.github/skills/agent-evolution-agent/scripts/audit-agent-quality.sh
```

## Bootstrapping New Repositories

1. **Use onboarding agent**: Invoke `repository-onboarding` agent
2. **Or manual setup**: Follow `.github/prompts/repository-onboarding.prompt.md`
3. **Or copy templates**: Extract from `.github/specs/agent-intelligence-framework.md`

→ **Extraction guide**: `.github/docs/TEMPLATE-EXTRACTION-GUIDE.md`

## Key References

| Resource | Location |
|----------|----------|
| Repository spec | `.github/specs/repository.md` |
| Agent framework | `.github/specs/agent-intelligence-framework.md` |
| Conventional tools | `.github/docs/conventional-tools.md` |
| Path-specific mechanism | `.github/docs/path-specific-instructions.md` |
