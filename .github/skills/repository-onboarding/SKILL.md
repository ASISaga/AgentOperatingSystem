---
name: repository-onboarding
description: Bootstrap GitHub Copilot agent intelligence system in new repositories with complete setup
license: MIT
metadata:
  author: ASISaga
  version: "1.0"
  category: automation
  role: bootstrap-specialist
allowed-tools: Bash(mkdir:*) Bash(cp:*) Read Edit Create
---

# Repository Onboarding Skill

**Role**: Bootstrap Specialist for Agent Intelligence Systems

Automated setup of complete GitHub Copilot agent intelligence system in new repositories based on templates and specifications.

## When to Use This Skill

Use this skill when:
- Setting up a new repository from scratch
- Adding agent intelligence to existing repository
- Migrating manual workflows to automated systems
- Standardizing repository structure across projects

## Core Principles

1. **Template-Based**: Use proven templates from specifications
2. **Technology-Aware**: Adapt to repository's tech stack
3. **Minimal Manual Work**: Automate as much as possible
4. **Validation First**: Ensure everything works before completion

## Workflows

### Workflow 1: New Repository Setup

**Purpose**: Bootstrap complete system in empty repository

**Steps**:
1. Create directory structure
2. Generate copilot-instructions.md from template
3. Create instruction files based on tech stack
4. Set up agents/prompts/skills
5. Create specs/docs
6. Configure validation
7. Verify setup

### Workflow 2: Existing Repository Enhancement

**Purpose**: Add agent intelligence to existing repository

**Steps**:
1. Backup existing .github/
2. Analyze existing structure
3. Integrate agent system
4. Migrate existing patterns
5. Validate integration

## Tool Integration

**Directory creation**:
```bash
mkdir -p .github/{instructions,specs,docs,agents,prompts,skills}
```

**Validation**:
```bash
./.github/skills/repository-onboarding/scripts/validate-setup.sh
```

## References

→ **Agent spec**: `.github/specs/agents.md` — Agent file format and conventions
→ **Prompt spec**: `.github/specs/prompts.md` — Prompt file format and conventions
→ **Skill spec**: `.github/specs/skills.md` — Skill file format and conventions
→ **Instructions spec**: `.github/specs/instructions.md` — Instruction file format and conventions
→ **Framework spec**: `.github/specs/agent-intelligence-framework.md` — Framework spec
→ **Onboarding prompt**: `.github/prompts/repository-onboarding.prompt.md` — Onboarding prompt
