---
applyTo: ".github/skills/*/SKILL.md"
description: "Coding standards for agent skill files (agentskills.io format)"
---

# Skill Files Instructions

## File Format

**YAML Frontmatter (required):**
```yaml
---
name: skill-name        # kebab-case, matches directory
description: One-sentence purpose with keywords (1-1024 chars)
license: MIT
metadata:
  author: ASISaga
  version: "2.1"
  category: design-system
  role: specialist-role
allowed-tools: Bash(npm:*) Read Edit
---
```

## Body Structure

1. Role and scope statement
2. Purpose paragraph
3. "When to Use This Skill" triggers
4. Core Principles or Responsibilities
5. Workflows and Examples
6. Tool Integration
7. Validation Instructions
8. Related Documentation

## Directory Structure

```
.github/skills/skill-name/
├── SKILL.md           # This file
├── scripts/           # Validation scripts
├── references/        # Detailed specs
└── assets/            # Visual examples (optional)
```

## Tool Integration

**Reference npm scripts:**
```bash
npm test
npm run test:scss
npm run lint:scss
```

**Validation scripts pattern:**
```bash
./.github/skills/[skill-name]/scripts/validate-*.sh
```

## Keep Concise

Detailed specifications belong in `references/` subdirectory, not in SKILL.md.

→ **Specifications**: `.github/specs/skills.md`
→ **Documentation**: `.github/docs/`
→ **agentskills.io spec**: https://agentskills.io

## Related Documentation

→ **Skill spec**: `.github/specs/skills.md` - Detailed skill file specification
→ **Framework**: `.github/docs/agent-intelligence-framework.md` - Framework specification
→ **Agent philosophy**: `.github/docs/agent-philosophy.md` - Design principles

---

**Version**: 1.1 - Added spec references for dogfooding  
**Last Updated**: 2026-02-14
