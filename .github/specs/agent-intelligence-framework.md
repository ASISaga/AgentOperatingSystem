---
applyTo: ".github/**/*.md,.github/**/*.prompt.md,.github/skills/**/*"
description: "Generic GitHub Copilot agent intelligence system: Ouroboros dogfooding, agents, prompts, skills, and instructions"
---

# GitHub Copilot Agent Intelligence System

**A reusable framework for establishing best-practice GitHub Copilot coding agent ecosystems**

## Philosophy: Ouroboros & Dogfooding

**AI agents SUPERCHARGE existing tools** (linters, validation scripts, npm commands, MCP servers) through continuous self-improvement:

- **Ouroboros Pattern**: Agents use and evolve themselves (meta-intelligence)
- **Dogfooding**: Build better by using what you build
- **Tool Leverage**: Orchestrate automation, never duplicate
- **Context Efficiency**: Eliminate redundancy, maximize signal

This creates a highly intelligent AI agent coding system where:
- Agents orchestrate existing automation
- Validation is automated via scripts
- Testing uses established npm workflows
- Tools are composed, not duplicated
- The system continuously improves itself

## Core Structure: Five Pillars

```
.github/
├── agents/           # 🔒 Internal coordination (protected, system-level)
├── instructions/     # 📋 Path-activated coding standards
├── prompts/          # 🤖 Agent task definitions
├── skills/           # 🛠️ Executable capabilities
└── copilot-instructions.md  # 🎯 High-level context (NO duplication)
```

### 1. Instructions (`instructions/*.instructions.md`)

**Path-activated coding standards** loaded by GitHub Copilot based on file patterns.

**Frontmatter pattern:**
```yaml
---
applyTo: "**/*.{ext},path/pattern/**"
description: "Brief description for agent discovery"
---
```

**Key principles:**
- **Glob patterns**: Activate automatically when matching files edited
- **No duplication**: Don't repeat what's in `copilot-instructions.md`
- **Specific guidance**: Language/framework-specific best practices
- **Tool integration**: Reference npm scripts, linters, validators

**Common instruction files:**
- `scss.instructions.md` → SCSS/CSS patterns
- `html.instructions.md` → HTML/Liquid/templating
- `js.instructions.md` → JavaScript patterns
- `docs.instructions.md` → Documentation standards
- `github-agent-system.instructions.md` → This file (agent ecosystem)

### 2. Prompts (`prompts/*.prompt.md`)

**Agent task definitions** with detailed instructions for specific workflows.

**YAML frontmatter:**
```yaml
---
description: "Brief agent purpose (1-256 chars)"
name: "agent_name"  # snake_case
agent: "agent"      # or "ask", "edit", custom
model: "claude-3-5-sonnet-20241022"
tools: ['*']        # All tools, or specific list
---
```

**Body structure:**
1. Agent role and purpose
2. Version enhancements (what's new)
3. Core responsibilities (actionable list)
4. When to use (activation triggers)
5. Workflows and examples
6. Tool integration (reference scripts)
7. Decision matrices (if applicable)
8. Related documentation
9. Version history footer

**Naming conventions:**
- File: `agent-name.prompt.md` (kebab-case)
- Name field: `agent_name` (snake_case)
- Clear, descriptive, discoverable

### 3. Skills (`skills/*/SKILL.md`)

**Executable, reusable capabilities** following [Agent Skills specification](https://agentskills.io).

**YAML frontmatter:**
```yaml
---
name: skill-name        # kebab-case, matches directory
description: One-sentence purpose with keywords (1-1024 chars)
license: MIT
metadata:
  author: YourOrg
  version: "2.1"
  category: category-name
  role: specialist-role
allowed-tools: Bash(npm:*) Read Edit
---
```

**Directory structure:**
```
.github/skills/skill-name/
├── SKILL.md           # Main definition
├── scripts/           # Automation & validation
│   └── validate-*.sh # Executable scripts
├── references/        # Detailed specs
│   └── *.md          # Static reference content
└── assets/            # Visual examples (optional)
```

**Body structure:**
1. Role and scope statement
2. Purpose paragraph
3. "When to Use This Skill" triggers
4. Core Principles or Responsibilities
5. Workflows and Examples
6. Tool Integration
7. Validation Instructions
8. Related Documentation

**Categories** (customize to your domain):
- `automation` - Scripts and workflows
- `documentation` - Content and guides
- `testing` - Quality assurance
- `meta-intelligence` - Self-improvement

**Roles** (customize to your needs):
- `lead-architect` - System-wide governance
- `specialist` - Domain-specific expertise
- `expert` - Deep technical knowledge

### 4. Agents (`agents/`)

**Protected directory** for internal agent coordination logic and system configuration.

**Purpose:**
- Agent handoff rules and coordination
- System-level feature toggles
- Internal performance metrics
- Cross-agent state management

**Access restrictions:**
- ✅ Accessible during meta-intelligence tasks
- ❌ Hidden during normal task execution
- Prevents context contamination
- Maintains clean task/system separation

**Directory structure:**
```
.github/agents/
├── README.md        # Access guidelines
└── [configs].yml    # As needed for coordination
```

### 5. copilot-instructions.md

**High-level context ONLY** - detailed instructions live in path-specific files.

**Content:**
- Repository purpose and role
- Key architectural concepts
- Quick reference tables
- Pointers to detailed instructions
- **NO duplication** of instruction file content

## Quick Start Templates

### Agent Prompt Template

```yaml
---
description: "Agent purpose in 1-256 chars"
name: "agent_name"
agent: "agent"
model: "claude-3-5-sonnet-20241022"
tools: ['*']
---

# Agent Name

**Version**: 1.0.0 - Initial implementation  
**Last Updated**: YYYY-MM-DD

## Role

[One paragraph describing agent's purpose and scope]

## Core Responsibilities

- [ ] Responsibility 1
- [ ] Responsibility 2
- [ ] Responsibility 3

## When to Use

Use this agent when:
- Condition 1
- Condition 2
- Condition 3

## Workflows

### Workflow 1

1. Step 1
2. Step 2
3. Step 3

## Tool Integration

**npm scripts:**
```bash
npm test
npm run lint
```

**Validation scripts:**
```bash
./.github/skills/skill-name/scripts/validate-*.sh
```

## Related Documentation

- `docs/path/to/spec.md` - Complete specification
- `.github/instructions/category.instructions.md` - Coding standards

---

**Version History:**
- 1.0.0 (YYYY-MM-DD) - Initial implementation
```

### Agent Skill Template

```yaml
---
name: skill-name
description: One-sentence purpose with discoverable keywords
license: MIT
metadata:
  author: YourOrg
  version: "1.0"
  category: category
  role: specialist
allowed-tools: Bash(npm:*) Read Edit
---

# Skill Name

**Role**: [Specialist/Expert/etc.] in [domain]

[One paragraph describing skill's purpose and scope]

## When to Use This Skill

Use this skill when:
- Scenario 1
- Scenario 2
- Scenario 3

## Core Principles

1. **Principle 1**: Description
2. **Principle 2**: Description
3. **Principle 3**: Description

## Workflows

### Workflow 1: Task Name

**Purpose**: [Brief description]

**Steps:**
1. Step 1
2. Step 2
3. Step 3

**Example:**
```bash
# Command examples
npm run test
```

## Tool Integration

**Required tools:**
- `npm test` - Description
- `npm run lint` - Description

**Validation scripts:**
```bash
./.github/skills/skill-name/scripts/validate-pattern.sh path/to/file
```

## Validation

All changes must pass:

1. **Automated validation:**
   ```bash
   ./.github/skills/skill-name/scripts/validate-*.sh
   ```

2. **npm scripts:**
   ```bash
   npm test
   ```

3. **Manual checks:**
   - Check 1
   - Check 2

## Related Documentation

- `docs/specs/specification.md` - Complete API reference
- `.github/instructions/category.instructions.md` - Coding standards
- `.github/prompts/related-agent.prompt.md` - Related workflow
```

## MANDATORY RULES

### File Naming
- **Prompts**: `agent-name.prompt.md` (kebab-case files, snake_case name field)
- **Skills**: `skill-name/SKILL.md` (kebab-case directory, matches name field)
- **Instructions**: `category.instructions.md` (lowercase, descriptive)

### YAML Frontmatter
- ✅ All prompt and skill files MUST have valid YAML frontmatter
- ✅ Required fields must be present
- ✅ Proper quoting and escaping
- ✅ Validate before committing

### Tool Declaration
- ✅ Explicitly list tools in frontmatter
- ✅ Use scoped patterns when applicable: `Bash(npm:*)`, `Bash(git:*)`
- ✅ Document why each tool is needed

### No Duplication
- ❌ Don't repeat `copilot-instructions.md` in instruction files
- ❌ Don't duplicate tool functionality (use npm scripts)
- ❌ Don't overlap agent responsibilities
- ❌ Don't create redundant validation scripts

### Tool Integration
- ✅ Reference existing npm scripts
- ✅ Create validation scripts in `skills/*/scripts/`
- ✅ Integrate with existing linters
- ✅ Return proper exit codes (0 = success)

## Validation Workflow

**Before committing:**

1. **YAML validation:**
   ```bash
   # Check frontmatter is valid
   python -c "import yaml; yaml.safe_load(open('.github/prompts/agent.prompt.md').read().split('---')[1])"
   ```

2. **Naming conventions:**
   - Prompts: snake_case name field, kebab-case file
   - Skills: kebab-case everywhere, directory matches name
   - Instructions: lowercase, `.instructions.md` suffix

3. **Run project tests:**
   ```bash
   npm test
   ```

4. **Test validation scripts:**
   ```bash
   ./.github/skills/*/scripts/validate-*.sh
   ```

5. **Check for duplication:**
   - Compare with `copilot-instructions.md`
   - Ensure unique agent responsibilities
   - Verify tool integration, not reimplementation

## Anti-Patterns

### ❌ DON'T

1. **Duplicate tool functionality**
   ```bash
   # DON'T create custom SCSS validator
   # DO reference npm run lint:scss
   ```

2. **Overlap agent responsibilities**
   - Each agent should have clear, non-overlapping scope
   - Coordinate via handoffs, not duplication

3. **Put static content in SKILL.md**
   - Use `references/*.md` for detailed specs
   - Keep SKILL.md focused on workflows

4. **Validate without scripts**
   - Always create executable `scripts/validate-*.sh`
   - Integrate existing tools, don't reimplement

5. **Skip tool declarations**
   - Always list tools in frontmatter
   - Document scoped access patterns

### ✅ DO

1. **Reference npm scripts**
   ```markdown
   Run validation:
   ```bash
   npm test
   npm run lint:scss
   ```
   ```

2. **Clear agent boundaries**
   - Define specific triggers for each agent
   - Document handoff patterns

3. **Offload to references/**
   - Detailed specs → `references/specification.md`
   - Examples → `references/examples.md`
   - Keep SKILL.md concise

4. **Automate via scripts/**
   - Validation logic → `scripts/validate-*.sh`
   - Make scripts executable
   - Return proper exit codes

5. **Maintain version history**
   ```markdown
   **Version**: X.Y.Z - Enhancement  
   **Last Updated**: YYYY-MM-DD
   ```

## Documentation Governance

### Version Tracking

All agent files should include:

```markdown
**Version**: X.Y.Z - Description  
**Last Updated**: YYYY-MM-DD  
**Status**: Active | Draft | Deprecated
```

### Core Documentation Files

Maintain ecosystem-level documentation:

- `.github/docs/` - Complete architecture (~600 lines typical)
- `.github/docs/agent-system-overview.md` - Agent catalog and navigation
- Additional files as needed for your domain

### Update Pattern

1. Update inline, don't create new versions
2. Add version header for significant changes
3. Maintain version history at end
4. Update "Last Updated" date
5. Cross-reference related docs

## Context Window Optimization

**Key strategies for maximum efficiency:**

### 1. Path-Specific Instructions

Instructions activate only when relevant files are edited:
```yaml
---
applyTo: "**/*.scss,_sass/**"
---
```

### 2. No Duplication Rule

- **copilot-instructions.md**: High-level context only
- **instructions/*.md**: Detailed, path-specific guidance
- **NEVER** repeat between the two

### 3. Reference, Don't Inline

```markdown
→ **Complete guide**: `/docs/specifications/detailed-spec.md`
→ **All scripts**: `.github/skills/agent/scripts/README.md`
```

### 4. Lean Frontmatter

```yaml
# Minimal but complete
---
description: "Brief (1-256 chars max)"
name: "agent_name"
agent: "agent"
model: "claude-3-5-sonnet-20241022"
tools: ['*']
---
```

### 5. Structured Brevity

Use tables, lists, and diagrams instead of prose:

| Pattern | Description |
|---------|-------------|
| Quick ref | Maximum info, minimum words |

## Tool Integration Patterns

### npm Scripts (REQUIRED)

**Always reference, never reimplement:**

```bash
npm test              # All tests
npm run test:build    # Build validation
npm run lint          # All linters
npm run lint:fix      # Auto-fix
```

**In prompts/skills:**
```markdown
Run validation:
```bash
npm test
```
```

### Validation Scripts (REQUIRED)

**Pattern:** `skills/*/scripts/validate-*.sh`

**Requirements:**
- Executable: `chmod +x`
- Exit codes: `0` = success, non-zero = failure
- Clear error messages
- Integration with existing tools

**Example:**
```bash
#!/bin/bash
# .github/skills/skill-name/scripts/validate-pattern.sh

set -e

FILE="$1"

if [ -z "$FILE" ]; then
  echo "Usage: $0 <file>"
  exit 1
fi

# Use existing tool
npm run lint:check "$FILE"

exit $?
```

### Linters & Checkers

**Integrate with existing configuration:**

- Configuration files: `.eslintrc.json`, `.stylelintrc.json`, etc.
- Built-in compilers: `tsc`, `sass`, `babel`
- Custom validators: Project-specific scripts

**Never duplicate linter logic** - always call via bash.

## MCP Server Integration (Optional)

If MCP servers are configured:

```yaml
---
tools: ['mcp-server-name/*']  # All tools from server
---
```

**Document available servers in your copilot-instructions.md**

## Ouroboros Self-Improvement

**Meta-intelligence pattern:**

1. **Use the system** - Agents perform tasks
2. **Track metrics** - Quality, efficiency, context usage
3. **Identify gaps** - Where agents struggle
4. **Evolve system** - Add/refine agents, prompts, skills
5. **Repeat** - Continuous improvement loop

**Implementation:**

Create a meta-intelligence agent that:
- Reviews agent performance
- Identifies improvement opportunities
- Proposes system enhancements
- Updates documentation
- Tracks evolution history

**Example agent:** `agent-evolution-agent`

## Repository Adaptation Guide

To use this system in your repository:

### 1. Copy Base Structure

```bash
# Copy from a reference repository
cp -r /reference/.github/instructions/ .github/
cp -r /reference/.github/prompts/ .github/
cp -r /reference/.github/skills/ .github/
```

### 2. Customize copilot-instructions.md

Replace with your repository's:
- Purpose and role
- Architecture overview
- Key concepts
- Quick references

### 3. Adapt Instruction Files

Update `instructions/*.instructions.md`:
- Keep generic patterns
- Add domain-specific guidance
- Update tool references (npm scripts)
- Adjust glob patterns

### 4. Create Domain Agents

Add prompts/skills for your domain:
- Identify key workflows
- Define agent responsibilities
- Create validation scripts
- Document integration

### 5. Remove Repository-Specific Content

Delete or adapt content that's specific to source repo:
- Domain-specific examples
- Project-specific tools
- Custom workflows

### 6. Test & Validate

```bash
npm test
./.github/skills/*/scripts/validate-*.sh
```

## Related Documentation

**This instruction file provides generic framework. For repository-specific guidance:**

→ **Repository-specific patterns**: Other instruction files in `.github/instructions/`  
→ **Complete guidelines**: `/docs/specifications/github-copilot-agent-guidelines.md` (if exists)  
→ **Ecosystem architecture**: `.github/.github/docs/agent-philosophy.md` (if exists)

---

**Applies to**: `.github/**/*.md`, `.github/**/*.prompt.md`, `.github/skills/**/*`  
**Version**: 2.0.0 - Generic reusable framework (extracted from theme-specific v1.5)  
**Last Updated**: 2026-02-13  
**License**: MIT - Free to copy and adapt for any repository
