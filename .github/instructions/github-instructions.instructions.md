---
applyTo: ".github/instructions/*.md"
description: "Coding standards for instruction files in .github/instructions/"
---

# Instruction Files Standards

## Purpose

Instruction files in `.github/instructions/` are **path-activated coding standards** that auto-load when editing files matching their `applyTo` glob patterns.

## File Format

**YAML Frontmatter (required):**
```yaml
---
applyTo: "glob/pattern/**"
description: "Brief description for agent discovery"
---
```

## Requirements

- **applyTo**: Specific glob pattern targeting exact file types
- **description**: One-line purpose (helps agents discover context)
- **Body**: Minimal coding standards, reference specs/docs for details

## Content Guidelines

✅ **DO Include:**
- File format requirements
- Coding standards specific to the file type
- Tool integration commands (npm scripts, validation scripts)
- References to specs/docs for detailed patterns

❌ **DON'T Include:**
- Detailed specifications (belong in `.github/specs/`)
- Implementation guides (belong in `.github/docs/`)
- Duplicate content from copilot-instructions.md
- Overly broad applyTo patterns

## Example Structure

```markdown
---
applyTo: "**/*.example"
description: "Standards for example files"
---

# Example Files Instructions

## File Format
[Format requirements]

## Tool Integration
```bash
npm run validate
```

## References
→ **Specification**: `.github/specs/example-spec.md`
```

## Validation

Before committing:
1. YAML frontmatter is valid
2. applyTo pattern is specific and focused
3. Content references specs/docs, doesn't duplicate
4. No overlap with other instruction files

## Related Documentation

→ **Instructions spec**: `.github/specs/instructions.md` - Detailed instruction file specification
→ **Framework**: `.github/docs/agent-intelligence-framework.md` - Complete system specification
→ **Path-specific instructions**: `.github/docs/path-specific-instructions.md` - How glob patterns work

---

**Version**: 1.1 - Added spec references for dogfooding  
**Last Updated**: 2026-02-14
