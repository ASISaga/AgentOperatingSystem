# Documentation Standards Guide

**Version**: 2.0.0  
**Last Updated**: 2026-03-07

Complete documentation standards for the BusinessInfinity repository. This guide complements `.github/instructions/docs.instructions.md` with detailed examples and patterns.

## Table of Contents

1. [File Naming Conventions](#file-naming-conventions)
2. [Version Update Patterns](#version-update-patterns)
3. [Quality Standards](#quality-standards)
4. [Anti-Patterns](#anti-patterns)
5. [Progressive Enhancement](#progressive-enhancement)

## File Naming Conventions

### Active Documentation

**Guides** (`/docs/guides/`):
- `FEATURE-GUIDE.md` - Uppercase for primary guides
- `feature-guide.md` - Lowercase acceptable for secondary guides
- Examples: `QUICK-START.md`, `deployment-guide.md`, `workflow-guide.md`

**Specifications** (`/docs/specifications/`):
- `feature.md` - Lowercase preferred
- Descriptive names over abbreviations
- Examples: `architecture.md`, `build-deployment.md`, `agent-self-learning-system.md`

**References** (`/docs/references/`):
- `FEATURE-REFERENCE.md` - Uppercase for main references
- Quick reference sheets and cheat sheets
- Examples: `WORKFLOW-REFERENCE.md`, `API-REFERENCE.md`

**Systems** (`/docs/systems/`):
- Domain-organized subdirectories as needed
- Follow same naming as specifications within

### Archived Documentation

**Implementations** (`/docs/archive/implementations/`):
- `FEATURE-IMPLEMENTATION.md` - Summary of completed work
- `FEATURE-v2.3.0.md` - Version-specific records
- Include version if multiple implementations exist

**Audits** (`/docs/archive/audits/`):
- `FEATURE-AUDIT-REPORT.md` - Quality assessments
- `FEATURE-FIX-SUMMARY.md` - Fix records

**Refactorings** (`/docs/archive/refactorings/`):
- `FEATURE-REFACTORING.md` - Major refactor summaries
- `FEATURE-MIGRATION.md` - Migration guides

### Naming Anti-Patterns

❌ **AVOID:**
- `FINAL-feature.md` - Status should be inside file
- `feature-COMPLETE.md` - Redundant suffix
- `feature-SUMMARY-v2.md` - Version in filename (use inside)
- `feature-PART-2.md` - Multi-part docs (consolidate instead)
- `feature-NEW.md` / `feature-OLD.md` - Use version control
- `temp-feature.md` - No temporary docs in repo

✅ **PREFER:**
- `feature.md` with version inside
- Single comprehensive document
- Proper archival for old versions

## Version Update Patterns

### Standard Version Header

```markdown
# Feature Guide

**Version**: 2.1.0  
**Last Updated**: 2026-02-10

## Version History

### v2.1.0 (2026-02-10)
- Added responsive layout patterns
- Enhanced touch target compliance
- Updated code examples

### v2.0.0 (2026-01-15)
- Initial ontological implementation
- Complete system redesign

## [Main content starts here]
```

### Minimal Version Info

For smaller docs without major versioning:

```markdown
# Quick Reference

*Last Updated: 2026-02-10*

[Content...]
```

### Version History Guidelines

**When to add version history:**
- Specifications that evolve over time
- Guides with breaking changes
- System documentation with multiple releases

**When to skip:**
- Simple how-tos without significant changes
- Archive documents (already versioned)
- Reference docs that are rarely updated

## Quality Standards

Every documentation file should meet these criteria:

### 1. Clear Purpose

**Single Responsibility:**
```markdown
# ✅ Good: Business Workflow Specification
Complete guide to the AOS orchestration workflow patterns

# ❌ Bad: General Development Guide
(Too broad - covers workflows, deployment, testing, etc.)
```

**Purpose Statement:**
- First paragraph explains what this document covers
- Clearly states audience (users, developers, maintainers)
- Defines scope boundaries

### 2. Discoverability

**Linked from Navigation:**
- Listed in `/docs/README.md` or `/docs/INDEX.md`
- Cross-referenced from related documents
- Included in relevant guides/specs

**Example Cross-Reference:**
```markdown
## Related Documentation

- [Business Workflows Spec](specifications/workflows.md)
- [Enterprise Capabilities](specifications/enterprise-capabilities.md)
- [Architecture Overview](specifications/architecture.md)
```

### 3. Maintainability

**Update, Don't Replace:**
```markdown
# ✅ Good Approach
## New Feature (Added 2026-02-10)
Details about the new feature...

# ❌ Bad Approach
Creating: FEATURE-UPDATE-2026-02-10.md
(Should update existing FEATURE.md instead)
```

**Version Tracking:**
- Update "Last Updated" date
- Add entry to Version History (if exists)
- Update affected code examples

### 4. Accuracy

**Code Examples:**
- Test all code examples
- Use real file paths
- Show complete, working code
- Include imports/dependencies

```markdown
# ✅ Good Example
\`\`\`python
from aos_client import AOSApp, WorkflowRequest

app = AOSApp(name="business-infinity")

@app.workflow("strategic-review")
async def strategic_review(request: WorkflowRequest) -> dict:
    agents = await request.client.list_agents()
    status = await request.client.start_orchestration(
        agent_ids=[a.agent_id for a in agents],
        purpose="Drive strategic review and continuous organisational improvement",
        purpose_scope="C-suite strategic alignment and cross-functional coordination",
        context=request.body,
    )
    return {"orchestration_id": status.orchestration_id}
\`\`\`

# ❌ Bad Example
\`\`\`python
# Incomplete, won't work
async def my_workflow(request):
    agents = list_agents()  # Missing await, wrong call
\`\`\`
```

**File Paths:**
- Use absolute paths from repo root: `/docs/specifications/`
- Or relative from current file: `../specifications/`
- Never use broken or hypothetical paths

### 5. Completeness

**Cover the Full Topic:**
- Include all necessary sections
- Provide enough examples
- Address common questions
- Link to related topics

**Minimum Sections:**
```markdown
# Feature Guide

## Overview
What is this feature?

## When to Use
Appropriate use cases

## Quick Start
Minimal working example

## Detailed Usage
Complete feature coverage

## Common Patterns
Real-world examples

## Troubleshooting
Common issues and solutions

## Related Documentation
Cross-references
```

## Anti-Patterns

### Pattern: Incremental Summaries

❌ **DON'T:**
```
docs/
  FEATURE-SUMMARY.md
  FEATURE-SUMMARY-PART-2.md
  FEATURE-SUMMARY-FINAL.md
  FEATURE-COMPLETE.md
```

✅ **DO:**
```
docs/
  specifications/feature.md  (updated progressively)
  
archive/implementations/
  FEATURE-IMPLEMENTATION.md  (completed work)
```

### Pattern: Version-Named Files

❌ **DON'T:**
```
docs/
  workflows-v1.0.md
  workflows-v2.0.md
  workflows-v2.1.md
```

✅ **DO:**
```
docs/
  specifications/workflows.md  (current version inside)

archive/implementations/
  WORKFLOWS-v1.0-MIGRATION.md  (if needed for historical reference)
```

### Pattern: Scattered Guides

❌ **DON'T:**
```
docs/
  workflow-intro.md
  workflow-basics.md
  workflow-advanced.md
  workflow-tips.md
```

✅ **DO:**
```
docs/
  specifications/workflows.md  (comprehensive, all levels)
```

## Progressive Enhancement

### Adding New Sections

When adding new content to existing docs:

```markdown
# Existing Feature Guide

[Existing content...]

## New Feature Name (Added 2026-02-10)

Description of new functionality...

### Quick Example
[Code example...]

### Detailed Usage
[Full documentation...]
```

Update metadata:
```markdown
**Version**: 2.1.0  
**Last Updated**: 2026-02-10

## Version History

### v2.1.0 (2026-02-10)  <-- Add this
- Added New Feature Name
- Enhanced existing examples
```

### Updating Code Examples

Replace inline, don't create new files:

```markdown
# Before (v1.0.0)
\`\`\`python
async def strategic_review(request):
    agents = await request.client.list_agents()
    return {"agents": [a.agent_id for a in agents]}
\`\`\`

# After (v2.0.0) - Update in place
\`\`\`python
@app.workflow("strategic-review")
async def strategic_review(request: WorkflowRequest) -> dict:
    agents = await request.client.list_agents()
    status = await request.client.start_orchestration(
        agent_ids=[a.agent_id for a in agents],
        purpose="Drive strategic review",
        context=request.body,
    )
    return {"orchestration_id": status.orchestration_id}
\`\`\`
```

Add version note if breaking change:
```markdown
**Changed in v2.0.0**: Now uses `start_orchestration` for perpetual workflows.
```

### Expanding Sections

Add depth to existing sections:

```markdown
## Existing Section

[Original content...]

### New Subsection (Enhanced 2026-02-10)

Additional details and examples...
```

## Pre-Commit Checklist

Before committing documentation:

- [ ] Checked if existing doc can be updated instead of creating new
- [ ] Added/updated version information
- [ ] Updated "Last Updated" date
- [ ] Updated table of contents if structure changed
- [ ] Verified all internal links work
- [ ] Cross-referenced related documentation
- [ ] Tested all code examples
- [ ] Moved completed work to archive if applicable
- [ ] Updated `/docs/README.md` navigation if needed
- [ ] No redundant content created
- [ ] Ran validation scripts

## Validation Scripts

Use these scripts before committing:

```bash
# Structure validation
./.github/skills/documentation-manager-agent/scripts/validate-doc-structure.sh

# Link validation
./.github/skills/documentation-manager-agent/scripts/validate-doc-links.sh docs/

# Redundancy check
./.github/skills/documentation-manager-agent/scripts/detect-doc-redundancy.sh

# Metadata validation
./.github/skills/documentation-manager-agent/scripts/check-doc-metadata.sh docs/specifications/
```

## Related Documentation

- [Archival Workflow Guide](ARCHIVAL-WORKFLOW.md) - Moving docs to archive
- `/docs/specifications/architecture.md` - System organization
- `.github/instructions/docs.instructions.md` - Core standards

**Version**: 1.0.0  
**Last Updated**: 2026-02-10
