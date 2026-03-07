# Agent System Specifications

This directory contains specifications and frameworks for the agent intelligence system.

## Files

### Agent Intelligence System Specifications

- **`agents.md`** - Specification for GitHub Copilot Custom Agent files (`.github/agents/*.agent.md`)
  - YAML frontmatter requirements and required fields
  - Naming conventions and prompt content structure
  - Relationship between agent, prompt, and skill files

- **`prompts.md`** - Specification for GitHub Copilot prompt files (`.github/prompts/*.prompt.md`)
  - YAML frontmatter requirements and required fields
  - Body structure and tool integration patterns
  - Naming conventions and lean content guidelines

- **`skills.md`** - Specification for GitHub Copilot skill files (`.github/skills/*/SKILL.md`)
  - YAML frontmatter requirements following agentskills.io
  - Directory structure, categories, and roles
  - Validation script patterns

- **`instructions.md`** - Specification for path-specific instruction files (`.github/instructions/*.instructions.md`)
  - YAML frontmatter with `applyTo` glob patterns
  - Content guidelines and the lean principle
  - Naming conventions

- **`agent-intelligence-framework.md`** - Complete reusable framework for establishing Copilot agent ecosystems
  - Five-pillar structure (agents, instructions, prompts, skills, copilot-instructions.md)
  - Tool leverage patterns (reference, don't duplicate)
  - Validation workflows
  - Context window optimization

- **`spec-driven-development.md`** - Specification-Driven Development (SDD) principles and agent workflows
  - Three SDD workflows via Spec Manager Agent (Specify → Plan → Tasks)
  - Feature directory structure (`specs/NNN-slug/`)
  - Constitutional principles (Nine Articles) and gate definitions
  - Validation scripts and quality standards

### Repository-Specific Specifications

- **`repository.md`** - Repository-specific spec (one per repository, same standard name)
  - Repository name, description, and role in the ecosystem
  - Technology stack and coding patterns
  - Testing and validation workflows
  - Key design principles for agents and contributors

- **`workflows.md`** - Business orchestration workflow specifications
  - Core workflows: `strategic-review`, `market-analysis`, `budget-approval`
  - C-suite agent selection pattern and fallback strategy
  - Reusable `c_suite_orchestration` workflow template
  - Orchestration update handler pattern and workflow variants

- **`enterprise-capabilities.md`** - Enterprise capability workflow specifications
  - Knowledge management (`knowledge-search`)
  - Risk governance (`risk-register`, `risk-assess`)
  - Decision audit trail (`log-decision`)
  - Business covenants (`covenant-create`)
  - Agent interaction (`ask-agent`)
  - MCP server integration (`mcp-orchestration`, `erp-search`)

## Purpose

Specifications define **how** systems work and **what** patterns to follow. Unlike instructions (which are path-activated for specific file types), specs are reference documents providing detailed technical specifications.

New feature specs are created using the Spec Manager Agent and its three SDD workflows.

→ **Create a spec**: `.github/agents/spec-manager.agent.md`
→ **SDD workflow**: `.github/specs/spec-driven-development.md`

## Usage

Reference these specs when:
- Creating new agents, prompts, or skills
- Understanding system architecture
- Implementing validation workflows
- Adapting system to new repositories
- Learning repository-specific patterns
- Creating or updating feature specifications

→ **Agent philosophy**: `.github/docs/agent-philosophy.md`
→ **Documentation**: `.github/docs/`
→ **Instructions**: `.github/instructions/`
