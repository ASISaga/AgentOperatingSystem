# Generic GitHub Copilot Agent Intelligence Template

**Extract and adapt the generic framework for your repository**

This guide explains how to use `github-agent-system.instructions.md` as a template for establishing a best-practice GitHub Copilot agent intelligence system in any repository.

## What You Get

The generic framework provides:

✅ **Complete 5-pillar structure** (agents, instructions, prompts, skills, copilot-instructions.md)  
✅ **Ouroboros & dogfooding philosophy** for continuous improvement  
✅ **Ready-to-use templates** for agents, prompts, and skills  
✅ **Validation workflows** integrated with existing tools  
✅ **Context window optimization** strategies  
✅ **MIT License** - Free to copy and adapt

## Quick Start

### Step 1: Copy the Generic Framework

```bash
# Navigate to your repository
cd /path/to/your-repo

# Create instructions directory
mkdir -p .github/instructions

# Copy the generic framework
cp /path/to/theme/.github/instructions/github-agent-system.instructions.md \
   .github/instructions/
```

### Step 2: Create Basic Structure

```bash
# Create agent ecosystem directories
mkdir -p .github/agents
mkdir -p .github/prompts
mkdir -p .github/skills

# Add README files
cat > .github/agents/README.md << 'EOF'
# Agent Internal Coordination

Protected directory for system-level configuration.

**Access**: Meta-intelligence tasks only  
**Purpose**: Agent handoff rules, feature toggles, performance metrics
EOF

cat > .github/prompts/README.md << 'EOF'
# Agent Prompts

Task definitions with detailed instructions for AI agents.

See `..instructions/github-agent-system.instructions.md` for templates.
EOF

cat > .github/skills/README.md << 'EOF'
# Agent Skills

Executable, reusable capabilities following agentskills.io spec.

See `../instructions/github-agent-system.instructions.md` for templates.
EOF
```

### Step 3: Create copilot-instructions.md

```bash
cat > .github/copilot-instructions.md << 'EOF'
# Copilot Instructions for [Your Repository Name]

You are working in the **[Your Repository Name]** repository.

## Repository Role

[Brief description of what this repository does]

## Path-Specific Instructions

Detailed coding standards are in `.github/instructions/` and are automatically activated by file path:

- **`.github/instructions/github-agent-system.instructions.md`** — Agent intelligence framework
- Add more as needed for your tech stack

**DO NOT duplicate these instructions**. They are loaded automatically by GitHub Copilot based on file path.

## Quick Reference

[Add domain-specific quick reference tables]

## Key Concepts

[Add repository-specific concepts and architecture]

---

**Repository**: [URL]  
**Documentation**: `/docs/README.md`  
**Agent System**: `.github/instructions/github-agent-system.instructions.md`
EOF
```

### Step 4: Customize for Your Domain

Edit `.github/instructions/github-agent-system.instructions.md`:

1. **Update npm scripts references:**
   ```markdown
   ## Tool Integration Patterns
   
   ### npm Scripts (REQUIRED)
   
   ```bash
   npm test              # Your test command
   npm run lint          # Your linter
   npm run build         # Your build command
   ```
   ```

2. **Customize agent categories:**
   ```yaml
   metadata:
     category: your-category  # backend, frontend, data, etc.
     role: your-role          # developer, reviewer, tester, etc.
   ```

3. **Add domain-specific examples:**
   Replace generic examples with your technology stack patterns.

## Domain-Specific Instruction Files

Create instruction files for your tech stack:

### Python Repository Example

```bash
cat > .github/instructions/python.instructions.md << 'EOF'
---
applyTo: "**/*.py,**/*.pyi"
description: "Python coding standards and best practices"
---

# Python Instructions

## Code Style

**Follow PEP 8** with these project-specific additions:

- Use type hints for all public functions
- Docstrings in Google style
- Max line length: 100 characters

## Testing

```bash
pytest                    # Run all tests
pytest --cov             # With coverage
pytest -v -s tests/unit  # Unit tests only
```

## Linting

```bash
ruff check .             # Fast linting
mypy .                   # Type checking
black .                  # Auto-formatting
```

## Related Documentation

→ `/docs/PYTHON_STYLE_GUIDE.md`
EOF
```

### Node.js Repository Example

```bash
cat > .github/instructions/javascript.instructions.md << 'EOF'
---
applyTo: "**/*.{js,jsx,ts,tsx}"
description: "JavaScript/TypeScript coding standards"
---

# JavaScript/TypeScript Instructions

## Code Style

**Follow Airbnb style guide** with project modifications.

## Testing

```bash
npm test                 # Jest tests
npm run test:watch       # Watch mode
npm run test:e2e         # E2E tests
```

## Linting

```bash
npm run lint             # ESLint
npm run lint:fix         # Auto-fix
npm run type-check       # TypeScript
```

## Related Documentation

→ `/docs/JAVASCRIPT_GUIDE.md`
EOF
```

## Creating Your First Agent

### Step 1: Define the Need

Identify a repetitive workflow that would benefit from AI automation:
- Code reviews
- Documentation updates
- Test generation
- Refactoring tasks

### Step 2: Create Agent Prompt

```bash
cat > .github/prompts/code-reviewer.prompt.md << 'EOF'
---
description: "Automated code review focusing on best practices and potential issues"
name: "code_reviewer"
agent: "agent"
model: "claude-3-5-sonnet-20241022"
tools: ['*']
---

# Code Reviewer Agent

**Version**: 1.0.0 - Initial implementation  
**Last Updated**: 2026-02-13

## Role

Automated code review agent that analyzes pull requests and provides feedback on:
- Code quality and best practices
- Potential bugs and edge cases
- Performance considerations
- Security vulnerabilities

## Core Responsibilities

- [ ] Review changed files for code quality
- [ ] Check adherence to project coding standards
- [ ] Identify potential bugs and edge cases
- [ ] Suggest performance improvements
- [ ] Flag security concerns

## When to Use

Use this agent when:
- Reviewing pull requests
- Checking code quality before commit
- Learning project best practices
- Seeking improvement suggestions

## Workflows

### Code Review Workflow

1. Read changed files
2. Check against coding standards (`.github/instructions/`)
3. Run linters and tests
4. Analyze for common issues
5. Generate review comments

## Tool Integration

**Run linters:**
```bash
npm run lint
```

**Run tests:**
```bash
npm test
```

**Check types:**
```bash
npm run type-check
```

## Related Documentation

- `.github/instructions/` - Coding standards
- `/docs/CONTRIBUTING.md` - Contribution guidelines

---

**Version History:**
- 1.0.0 (2026-02-13) - Initial implementation
EOF
```

### Step 3: Create Agent Skill (Optional)

For reusable capabilities, create a skill:

```bash
mkdir -p .github/skills/code-reviewer

cat > .github/skills/code-reviewer/SKILL.md << 'EOF'
---
name: code-reviewer
description: Automated code review focusing on quality, security, and best practices
license: MIT
metadata:
  author: YourOrg
  version: "1.0"
  category: quality-assurance
  role: reviewer
allowed-tools: Bash(npm:*) Bash(git:*) Read
---

# Code Reviewer Skill

**Role**: Quality Assurance Reviewer

Automated code review capability that analyzes code changes for quality, security, and adherence to project standards.

## When to Use This Skill

Use this skill when:
- Reviewing pull requests
- Pre-commit quality checks
- Learning project conventions
- Identifying improvement opportunities

## Core Principles

1. **Automated First**: Use linters and tests before manual review
2. **Constructive Feedback**: Explain why, not just what
3. **Project Standards**: Follow `.github/instructions/` guidelines

## Workflows

### PR Review Workflow

1. **Run automated checks:**
   ```bash
   npm run lint
   npm test
   ```

2. **Review changed files:**
   - Check coding standards
   - Identify potential issues
   - Suggest improvements

3. **Generate feedback:**
   - Positive: What's done well
   - Issues: What needs fixing
   - Suggestions: How to improve

## Validation

All reviews must include:

1. **Automated validation:**
   ```bash
   npm run lint
   npm test
   ```

2. **Manual checks:**
   - Code readability
   - Edge cases covered
   - Documentation updated

## Related Documentation

- `../instructions/github-agent-system.instructions.md` - Agent framework
- `/docs/CODE_REVIEW_GUIDE.md` - Review guidelines (if exists)
EOF
```

## Validation Scripts

Add validation scripts to your skills:

```bash
mkdir -p .github/skills/code-reviewer/scripts

cat > .github/skills/code-reviewer/scripts/validate-code.sh << 'EOF'
#!/bin/bash
# Validate code quality

set -e

FILE="$1"

if [ -z "$FILE" ]; then
  echo "Usage: $0 <file>"
  exit 1
fi

echo "Running linters..."
npm run lint "$FILE"

echo "Running tests..."
npm test

echo "✅ Validation passed"
exit 0
EOF

chmod +x .github/skills/code-reviewer/scripts/validate-code.sh
```

## Context Window Optimization

### Prevent Duplication

**DON'T repeat in `copilot-instructions.md`:**
```markdown
<!-- ❌ DON'T DO THIS -->
# Copilot Instructions

## Python Coding Standards

Use PEP 8...
[50 lines of Python standards]
```

**DO reference instruction files:**
```markdown
<!-- ✅ DO THIS -->
# Copilot Instructions

## Path-Specific Instructions

- `.github/instructions/python.instructions.md` — Python standards
```

### Use References

**DON'T inline large specs:**
```markdown
<!-- ❌ DON'T DO THIS -->
## Complete API Reference

[200 lines of API documentation]
```

**DO reference documentation:**
```markdown
<!-- ✅ DO THIS -->
→ **Complete API reference**: `/docs/api/README.md`
```

## Testing Your Setup

### Verify Structure

```bash
tree .github
# Should show:
# .github/
# ├── agents/
# ├── instructions/
# ├── prompts/
# ├── skills/
# └── copilot-instructions.md
```

### Test Glob Patterns

Edit a file matching your `applyTo` pattern and verify GitHub Copilot loads the instructions.

### Run Validation

```bash
# Test npm scripts
npm test
npm run lint

# Test validation scripts
./.github/skills/*/scripts/*.sh
```

## Customization Examples

### Backend API Repository

```yaml
# Categories
metadata:
  category: backend-api
  role: api-developer

# Common tasks
- API endpoint creation
- Database schema updates
- Authentication logic
- API documentation
```

### Frontend Application

```yaml
# Categories
metadata:
  category: frontend-ui
  role: ui-developer

# Common tasks
- Component development
- State management
- Responsive design
- Accessibility compliance
```

### Data Pipeline

```yaml
# Categories
metadata:
  category: data-engineering
  role: pipeline-engineer

# Common tasks
- ETL pipeline development
- Data validation
- Performance optimization
- Monitoring setup
```

## Continuous Improvement (Ouroboros)

### Track What Works

Document successful agent patterns:
- Which agents save the most time?
- Which workflows are most reliable?
- What improvements emerged from usage?

### Evolve the System

1. **Use the agents** - Perform tasks
2. **Track metrics** - Quality, efficiency
3. **Identify gaps** - Where agents struggle
4. **Enhance system** - Add/refine agents
5. **Repeat** - Continuous loop

### Create Meta-Agent

Build an agent that improves the agent system:

```bash
cat > .github/prompts/agent-evolution.prompt.md << 'EOF'
---
description: "Meta-agent that evolves the agent intelligence system"
name: "agent_evolution"
agent: "agent"
model: "claude-3-5-sonnet-20241022"
tools: ['*']
---

# Agent Evolution Agent

Meta-intelligence agent that continuously improves the agent ecosystem.

## Responsibilities

- Review agent performance metrics
- Identify improvement opportunities
- Propose new agents/skills for gaps
- Update documentation
- Track evolution history
EOF
```

## Next Steps

1. ✅ Copy generic framework
2. ✅ Create basic structure
3. ✅ Customize for your domain
4. ✅ Create first agent
5. ✅ Add validation scripts
6. ✅ Test and iterate

## Resources

**Framework source:**
- `.github/docs/agent-intelligence-framework.md` - Complete framework guide
- `.github/specs/agent-intelligence-framework.md` - Framework specification

**Specifications:**
- `.github/specs/agents.md` - Agent file specification
- `.github/specs/prompts.md` - Prompt file specification
- `.github/specs/skills.md` - Skill file specification
- `.github/specs/instructions.md` - Instruction file specification
- [Agent Skills](https://agentskills.io) - agentskills.io specification
- [GitHub Copilot](https://docs.github.com/copilot) - Official docs

**This repository:**
- `.github/docs/agent-philosophy.md` - Ecosystem architecture
- `.github/docs/path-specific-instructions.md` - Path-specific mechanism

## Support

**Questions?**
- Review `.github/specs/agent-intelligence-framework.md`
- Check `.github/specs/` in this repository
- Create an issue in your repository

---

**Version**: 1.1.0 - Updated to reference dedicated spec files  
**Last Updated**: 2026-03-07  
**License**: MIT - Free to use and adapt
