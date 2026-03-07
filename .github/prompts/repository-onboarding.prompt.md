---
description: "Onboard new repositories with complete agent intelligence system"
name: "repository_onboarding"
agent: "agent"
model: "Auto"
tools: ['*']
---

# Repository Onboarding Agent

**Version**: 1.0.0  
**Last Updated**: 2026-02-14

## Role

Bootstrap complete GitHub Copilot agent intelligence system in new repositories based on templates and specifications.

## Core Responsibilities

- [ ] Create `.github/` directory structure
- [ ] Generate `copilot-instructions.md` from template
- [ ] Set up path-specific instruction files
- [ ] Create initial agents, prompts, and skills
- [ ] Configure validation and testing
- [ ] Establish documentation structure

## When to Use

Use this agent when:
- Setting up a new repository
- Adding agent intelligence to existing repository
- Migrating from manual to automated workflows
- Establishing coding standards and patterns

## Onboarding Workflow

### Step 1: Initialize Structure

Create directory structure:
```bash
mkdir -p .github/{instructions,specs,docs,agents,prompts,skills}
```

### Step 2: Generate copilot-instructions.md

Use template from `.github/specs/agent-intelligence-framework.md`:
- Repository-specific context (replace placeholders)
- Path-specific instruction references
- Architecture description
- Reference to specs/docs

**Template variables**:
- `{{REPO_NAME}}` - Repository name
- `{{REPO_PURPOSE}}` - What this repository does
- `{{TECH_STACK}}` - Technologies used
- `{{KEY_CONCEPTS}}` - Important concepts

### Step 3: Create Instruction Files

Based on technology stack, create:

**For all repositories**:
- `docs.instructions.md` - Documentation standards
- `github-instructions.instructions.md` - Instruction file standards
- `github-specs.instructions.md` - Spec file standards
- `github-docs.instructions.md` - Doc file standards

**For web projects**:
- `html.instructions.md` - HTML/template standards
- `css.instructions.md` or `scss.instructions.md` - Style standards
- `js.instructions.md` - JavaScript standards

**For specific stacks**:
- `python.instructions.md` - Python projects
- `typescript.instructions.md` - TypeScript projects
- `go.instructions.md` - Go projects

### Step 4: Create Initial Agents

Generate from templates:

**Code Review Agent** (`code-reviewer.agent.md`):
```yaml
---
name: code-reviewer
description: "Automated code review for quality and standards"
prompt: |
  Review code changes for:
  - Coding standards compliance
  - Best practices
  - Potential bugs
  - Performance issues
tools: ['*']
---
```

**Documentation Agent** (`documentation.agent.md`):
```yaml
---
name: documentation
description: "Maintain and validate documentation"
prompt: |
  Ensure documentation is:
  - Up to date
  - Complete
  - Well-organized
  - Properly linked
tools: ['*']
---
```

### Step 5: Create Initial Prompts

**Code Review Prompt** (`code-reviewer.prompt.md`):
- Detailed review criteria
- Tool integration (linters, tests)
- Reporting format

**Documentation Prompt** (`documentation.prompt.md`):
- Documentation standards
- Update workflows
- Validation steps

### Step 6: Create Initial Skills

**Code Review Skill** (`code-reviewer/SKILL.md`):
- Validation scripts in `scripts/`
- Reference documentation in `references/`

### Step 7: Set Up Specs

Create specification files:
- `architecture.md` - System architecture
- `coding-standards.md` - Coding conventions
- `testing-strategy.md` - Testing approach

### Step 8: Set Up Docs

Create documentation files:
- `getting-started-guide.md` - Quick start
- `development-guide.md` - Development workflow
- `api-reference.md` - API documentation (if applicable)

### Step 9: Configure Validation

Set up testing and linting:
```json
// package.json
{
  "scripts": {
    "test": "npm run lint && npm run test:unit",
    "lint": "eslint .",
    "test:unit": "jest"
  }
}
```

### Step 10: Verify Setup

Check that:
- [ ] All directories created
- [ ] copilot-instructions.md has no placeholders
- [ ] Instruction files have proper applyTo patterns
- [ ] Agents/prompts/skills are valid
- [ ] Specs/docs are referenced correctly
- [ ] Validation scripts work

## Tool Integration

**Reference these tools in instructions**:
```bash
npm test              # Run all tests
npm run lint          # Run linters
npm run build         # Build project
```

**Validation scripts pattern**:
```bash
./.github/skills/[skill-name]/scripts/validate-*.sh
```

## Templates

### copilot-instructions.md Template

```markdown
# Copilot Instructions for {{REPO_NAME}}

You are working in the **{{REPO_NAME}}** repository.

## Repository Purpose

{{REPO_PURPOSE}}

## Tech Stack

{{TECH_STACK}}

## Path-Specific Instructions

Detailed coding standards in `.github/instructions/`:

- `.github/instructions/[file].instructions.md` — [Standards]

## Key Concepts

{{KEY_CONCEPTS}}

## Agent Intelligence System

Directory Structure:
\```
.github/
├── copilot-instructions.md
├── instructions/
├── specs/
├── docs/
├── agents/
├── prompts/
└── skills/
\```

→ **Architecture**: `.github/specs/agent-intelligence-framework.md`
```

### Instruction File Template

```yaml
---
applyTo: "**/*.ext"
description: "Standards for EXT files"
---

# EXT Files Instructions

## File Format
[Format requirements]

## Coding Standards
[Standards specific to this file type]

## Tool Integration
\```bash
npm run validate:ext
\```

## References
→ **Specification**: `.github/specs/ext-spec.md`
```

## Validation

After onboarding:
1. Run `npm test` to verify setup
2. Check all instruction files have applyTo patterns
3. Verify specs/docs are properly linked
4. Test agent/prompt/skill files are valid
5. Ensure no duplicate content

## Related Documentation

→ **Agent spec**: `.github/specs/agents.md` — Agent file format and conventions
→ **Prompt spec**: `.github/specs/prompts.md` — Prompt file format and conventions
→ **Skill spec**: `.github/specs/skills.md` — Skill file format and conventions
→ **Instructions spec**: `.github/specs/instructions.md` — Instruction file format and conventions
→ **Framework spec**: `.github/specs/agent-intelligence-framework.md` — Framework templates
→ **Extraction guide**: `.github/docs/TEMPLATE-EXTRACTION-GUIDE.md` — How to adapt templates
→ **Agent philosophy**: `.github/docs/agent-philosophy.md` — Core principles

---

**Version History**:
- 1.1.0 (2026-02-14) - Added spec references for dogfooding
- 1.0.0 (2026-02-14) - Initial onboarding agent
