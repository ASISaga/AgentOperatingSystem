---
name: documentation-manager-agent
description: Manage documentation lifecycle, enforce standards, validate structure, detect redundancy, and ensure proper archival. Automate documentation quality checks with validation scripts. Use when creating, updating, or organizing documentation across the repository to maintain single source of truth and prevent documentation drift.
license: MIT
metadata:
  author: ASISaga
  version: "1.1"
  category: documentation
  role: documentation-specialist
allowed-tools: Bash Read Edit
---

# Documentation Manager Agent

**Role**: Documentation Quality and Organization Specialist  
**Scope**: All documentation in `/docs`, repository root, agent docs  
**Version**: 1.1 - High-Density Refactor

## Purpose

Ensure documentation follows organizational standards, remains maintainable, and avoids redundancy. Enforces principles from `.github/instructions/docs.instructions.md` through automated validation.

## When to Use This Skill

Activate when:
- Creating/updating documentation files
- Reorganizing documentation structure
- Moving completed work to archive
- Auditing documentation quality
- Checking for redundant content
- Validating cross-references/links

## Core Principles

**Update, Don't Replace:**
- ✅ Update existing files with new sections
- ✅ Add version headers for changes
- ❌ Don't create `FEATURE-v2.3.0.md` for every change

**Single Source of Truth:**
- ✅ Merge scattered guides
- ✅ Eliminate duplicates
- ❌ Don't duplicate content across files

**Proper Archival:**
- ✅ Move completed work to `/docs/archive/implementations/`
- ✅ Preserve historical reference
- ❌ Don't leave completed docs in active area

→ **Complete standards**: `.github/instructions/docs.instructions.md`

## Validation Scripts

### 1. Structure Validation

```bash
./.github/skills/documentation-manager-agent/scripts/validate-doc-structure.sh

# Checks:
# - Required files (README.md, INDEX.md)
# - Required directories
# - Misplaced files
# - Version-numbered files
```

### 2. Link Validation

```bash
./.github/skills/documentation-manager-agent/scripts/validate-doc-links.sh docs/

# Checks:
# - Broken internal links
# - Missing referenced files
# - Invalid anchor links
```

### 3. Redundancy Detection

```bash
./.github/skills/documentation-manager-agent/scripts/detect-doc-redundancy.sh

# Finds:
# - Similar filenames
# - Redundant naming patterns
# - Content similarity
# - Old/new file pairs
```

### 4. Metadata Validation

```bash
./.github/skills/documentation-manager-agent/scripts/check-doc-metadata.sh docs/specifications/

# Checks:
# - Version headers
# - "Last Updated" dates
# - Outdated timestamps
# - Versioning consistency
```

## Pre-Commit Workflow

```bash
# 1. Validate structure
./scripts/validate-doc-structure.sh

# 2. Check metadata
./scripts/check-doc-metadata.sh docs/path/to/file.md

# 3. Verify links
./scripts/validate-doc-links.sh docs/path/to/file.md

# 4. Check redundancy
./scripts/detect-doc-redundancy.sh
```

## Documentation Organization

**Active** (`/docs/`):
- `README.md` - Navigation index
- `guides/` - User-facing tutorials
- `specifications/` - Technical specs
- `references/` - Quick references
- `systems/` - System documentation

**Historical** (`/docs/archive/`):
- `implementations/` - Completed features
- `audits/` - Quality assessments
- `refactorings/` - Major refactors

→ **Complete organization**: `references/DOCUMENTATION-GUIDE.md`

## Resources

**Spec Files**:
- `.github/specs/agents.md` - Agent file specification
- `.github/specs/skills.md` - Skill file specification
- `.github/specs/instructions.md` - Instruction file specification
- `.github/specs/repository.md` - Repository structure and role

**Documentation Standards**:
- `references/DOCUMENTATION-GUIDE.md` - **Comprehensive standards**
- `references/ARCHIVAL-WORKFLOW.md` - **Archival process**
- `scripts/` - **All validation scripts**
- `.github/instructions/docs.instructions.md` - Core documentation standards
- `.github/docs/dogfooding-guide.md` - Self-improvement workflows

**Related Skills**: agent-evolution-agent, spec-manager

---

**Version History**:
- **v1.1** (2026-02-10): High-density refactor - 205→136 lines, enhanced spec references
- **v1.0** (2026-02-10): Initial documentation management system
