---
applyTo: "docs/**/*.md,*.md"
description: "Documentation standards for GitHub Copilot Custom Agent files"
---

# Documentation Instructions

## Core Principles

### 1. Update, Don't Replace
**NEVER create new summary/completion docs for every change.**
- Update existing documentation with new sections
- Add version headers for significant changes
- Use "Last Updated" dates to track currency
- Append to existing guides rather than creating new ones

### 2. Consolidate Similar Content
- Merge scattered guides into comprehensive ones
- Cross-reference related documentation
- Eliminate redundant files
- Maintain single source of truth

### 3. Progressive Enhancement
- Add new sections to existing guides
- Update code examples inline
- Expand existing sections rather than duplicate
- Keep historical context when relevant

### 4. Proper Archival
Completed implementation work:
- Move to `/docs/archive/implementations/`
- Don't delete - preserve for historical reference
- Link from main docs if still relevant
- Keep active docs current and actionable

## Documentation Structure

### Active Documentation (`/docs/`)

**Root Level** - Essential, living documentation:
- `README.md` - Documentation index and navigation
- Domain-specific guides (ontology, layout, semantic, etc.)
- Quick starts and references
- Current implementation guides

**`/docs/guides/`** - User-facing tutorials:
- Quick start guides, technical how-tos, best practices, tool documentation

**`/docs/specifications/`** - Technical specifications:
- System architecture, component specs, design tokens, API references

### Historical Documentation (`/docs/archive/`)

**`/docs/archive/implementations/`** - Completed work:
- Implementation summaries, version-specific enhancements, feature completion records

**`/docs/archive/audits/`** - Code audits:
- Quality assessments, fix summaries, before/after comparisons

**`/docs/archive/refactorings/`** - Major refactors:
- Refactoring summaries, breaking changes, migration paths

## When to Create New Documentation

### Create New When:
1. **New Feature/System** - Documenting something that doesn't exist yet
2. **New User Guide** - Tutorial for a distinct use case
3. **New Specification** - Formal spec for a new subsystem
4. **Major Version** - Breaking changes require new migration guide

### Update Existing When:
1. **Enhancing Existing Feature** - Add section to existing doc
2. **Bug Fixes/Improvements** - Update relevant sections
3. **Code Examples** - Replace outdated examples inline
4. **Clarifications** - Improve existing content
5. **New Patterns** - Add to existing pattern catalog

## Version Update Pattern

```markdown
# Feature Guide

*Last Updated: 2026-01-29 | Version 2.1.0*

## Version History

### v2.1.0 (2026-01-29)
- Added responsive layout patterns
- Enhanced touch target compliance

### v2.0.0 (2026-01-15)
- Initial ontological implementation

## [Rest of content, updated inline]
```

## Anti-Patterns to Avoid

### ❌ DON'T:
1. Create `IMPLEMENTATION-SUMMARY-FEATURE-v2.3.0.md` for every change
2. Create `VISUAL-SUMMARY-PART-2.md` instead of updating Part 1
3. Leave completed implementation docs in root
4. Create redundant "COMPLETE" or "FINAL" documents
5. Duplicate content across multiple files

### ✅ DO:
1. Update `docs/specifications/feature.md` with new version section
2. Expand existing visual guides with new examples
3. Move completed work to `archive/implementations/`
4. Update main documentation progressively
5. Consolidate related content

## File Naming Conventions

**Active Documentation:**
- Guides: `FEATURE-GUIDE.md` or `feature-guide.md`
- References: `FEATURE-REFERENCE.md`
- Specifications: `feature.md` (lowercase in `/specifications/`)

**Archived Documentation:**
- Implementations: `FEATURE-IMPLEMENTATION.md` or `FEATURE-v2.3.0.md`
- Audits: `FEATURE-AUDIT-REPORT.md`

**Avoid:**
- `FINAL-`, `COMPLETE-`, `SUMMARY-` prefixes on active docs
- Version numbers in active doc names (use inside doc)

## Pre-Commit Checklist

- [ ] Checked if existing doc can be updated instead
- [ ] Added version/date information
- [ ] Updated table of contents if needed
- [ ] Verified all internal links work
- [ ] Cross-referenced related documentation
- [ ] Moved completed work to archive if applicable
- [ ] Updated `docs/README.md` navigation if needed
- [ ] No redundant content created

## Quality Standards

Every documentation file should:
1. **Have a clear purpose** - Single responsibility
2. **Be discoverable** - Linked from README or relevant guide
3. **Be maintainable** - Updated, not replaced
4. **Be accurate** - Reflect current codebase
5. **Be complete** - Cover topic comprehensively

## Documentation References

**Core standards:**
- `/docs/specifications/architecture.md` - System architecture and organization
- `/docs/specifications/build-deployment.md` - Build and deployment processes

**Applies to**: `docs/**/*.md`, `*.md` in repository root  
**Version**: 1.1 - Added spec references for improved context efficiency  
**Last Updated**: 2026-02-10
