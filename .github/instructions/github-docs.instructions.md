---
applyTo: ".github/docs/*.md"
description: "Standards for documentation files in .github/docs/"
---

# Documentation Files Standards

## Purpose

Documentation files in `.github/docs/` are **implementation guides and references** that help users understand and use the agent intelligence system.

## File Naming

- Use kebab-case: `guide-name.md`
- Be descriptive: `agent-system-overview.md` not `overview.md`
- Include type: `getting-started-guide.md`, `api-reference.md`

## Content Structure

```markdown
# Documentation Title

**Last Updated**: YYYY-MM-DD  
**Audience**: [Developers | Contributors | Users]

## Introduction
[What this document covers]

## Prerequisites
[What you need to know before reading]

## Content
[Main documentation content]

## Examples
[Practical examples]

## Next Steps
[What to read/do next]

## References
[Related docs and specs]
```

## Content Guidelines

✅ **DO Include:**
- Step-by-step guides
- Tutorials and walkthroughs
- Usage examples
- Troubleshooting tips
- Quick reference materials

❌ **DON'T Include:**
- Detailed specifications (belong in `.github/specs/`)
- Path-specific coding standards (belong in `.github/instructions/`)
- Duplicate content from other docs

## Documentation Types

**Guides**: How to accomplish specific tasks
- `getting-started-guide.md`
- `migration-guide.md`

**References**: Quick lookup information
- `agent-quick-reference.md`
- `api-reference.md`

**Overviews**: System understanding
- `agent-system-overview.md`
- `architecture-overview.md`

## Cross-References

Docs should be:
- **Referenced from**: copilot-instructions.md, instruction files, specs
- **Reference**: Specs for technical details
- **Link to**: Other related docs

## Validation

Before committing:
1. Follows naming convention
2. Has clear audience and prerequisites
3. Examples are tested and work
4. Links to other docs/specs are correct
5. No duplication with specs or instructions

## Related Documentation

→ **Agent framework**: `.github/specs/agent-intelligence-framework.md` - Complete system specification  
→ **Architecture**: `/docs/specifications/architecture.md` - System architecture and organization  
→ **Agent guidelines**: `/docs/specifications/github-copilot-agent-guidelines.md` - Standards and best practices  
→ **Self-learning**: `/docs/specifications/agent-self-learning-system.md` - Dogfooding and Ouroboros  
→ **Agent philosophy**: `.github/docs/agent-philosophy.md` - Core principles

---

**Version**: 1.1 - Added spec references for dogfooding  
**Last Updated**: 2026-02-14
