---
applyTo: ".github/prompts/*.prompt.md"
description: "Coding standards for agent prompt files"
---

# Prompt Files Instructions

## File Format

**YAML Frontmatter (required):**
```yaml
---
description: "Brief agent purpose (1-256 chars)"
name: "agent_name"  # snake_case
agent: "agent"
model: "claude-3-5-sonnet-20241022"
tools: ['*']
---
```

## Body Structure

1. Agent role and purpose
2. Core responsibilities (actionable list)
3. When to use (activation triggers)
4. Workflows and examples
5. Tool integration
6. Related documentation

## Tool Integration

**Reference existing tools, never duplicate:**

```bash
npm test              # Run all tests
npm run test:scss     # SCSS compilation
npm run lint:scss     # Stylelint validation
```

**Validation scripts:**
```bash
./.github/skills/[skill-name]/scripts/validate-*.sh
```

## Keep Focused

Reference detailed patterns instead of duplicating:
→ **Specifications**: `.github/specs/prompts.md`
→ **Documentation**: `.github/docs/`

## Related Documentation

→ **Prompt spec**: `.github/specs/prompts.md` - Detailed prompt file specification
→ **Framework**: `.github/docs/agent-intelligence-framework.md` - Complete system framework
→ **Agent philosophy**: `.github/docs/agent-philosophy.md` - Core principles

---

**Version**: 1.1 - Added spec references for dogfooding  
**Last Updated**: 2026-02-14
