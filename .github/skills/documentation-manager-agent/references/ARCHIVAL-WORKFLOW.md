# Documentation Archival Workflow

**Version**: 1.0.0  
**Last Updated**: 2026-02-10

Complete guide to archiving documentation properly. This ensures historical preservation while keeping active documentation clean and current.

## Table of Contents

1. [When to Archive](#when-to-archive)
2. [Archive Structure](#archive-structure)
3. [How to Archive](#how-to-archive)
4. [Linking from Active Docs](#linking-from-active-docs)
5. [Best Practices](#best-practices)

## When to Archive

### Implementation Summaries

**Archive when:**
- Feature development is complete
- Implementation work is merged
- Summary served its purpose during development

**Example scenario:**
```
During development: /docs/FEATURE-IMPLEMENTATION.md
After merge: /docs/archive/implementations/FEATURE-IMPLEMENTATION.md
```

**Indicators to archive:**
- File name contains "IMPLEMENTATION", "SUMMARY", "COMPLETE"
- Describes completed development work
- No longer actively updated
- Still valuable for historical reference

### Version-Specific Documentation

**Archive when:**
- New major version is released
- Migration is complete
- Old version is deprecated

**Example:**
```
Before v2.0: /docs/WORKFLOWS-v1.0-GUIDE.md
After v2.0: /docs/archive/implementations/WORKFLOWS-v1.0-MIGRATION.md
Current: /docs/specifications/workflows.md (v2.0)
```

### Audit Reports

**Archive immediately after:**
- Fixes are implemented
- Report is reviewed and addressed
- Summary is created

**Example:**
```
After audit: /docs/archive/audits/AGENT-QUALITY-AUDIT-2026-01.md
Active doc: /docs/specifications/architecture.md (updated)
```

### Refactoring Documentation

**Archive when:**
- Refactoring is complete
- Migration is finished
- Breaking changes are documented

**Example:**
```
During refactor: /docs/WORKFLOW-REFACTORING-PLAN.md
After complete: /docs/archive/refactorings/WORKFLOW-REFACTORING-2026-02.md
```

### Do NOT Archive

**Keep active:**
- Specifications (always keep current version)
- Guides and tutorials (update instead)
- Quick references (update instead)
- System documentation (evolve in place)

## Archive Structure

### Directory Organization

```
/docs/archive/
├── implementations/      # Completed feature work
│   ├── WORKFLOW-IMPLEMENTATION.md
│   ├── WORKFLOW-v1.0-MIGRATION.md
│   └── PROJECT-COMPLETION-2026-01.md
│
├── audits/              # Code quality assessments
│   ├── AGENT-QUALITY-AUDIT-2026-01.md
│   ├── WORKFLOW-AUDIT-2026-Q1.md
│   └── PERFORMANCE-AUDIT-Q1-2026.md
│
└── refactorings/        # Major refactoring records
    ├── WORKFLOW-REFACTORING-2026-02.md
    ├── SDK-MIGRATION.md
    └── DOCUMENTATION-REORGANIZATION.md
```

### File Naming in Archive

**Implementations:**
- `FEATURE-IMPLEMENTATION.md` - General implementation summary
- `FEATURE-v2.0.md` - Version-specific implementation
- `PROJECT-NAME-COMPLETION.md` - Project completion record

**Audits:**
- `COMPONENT-AUDIT-YYYY-MM.md` - Dated audit reports
- `FEATURE-FIX-SUMMARY.md` - Fix implementation summary
- `QUALITY-ASSESSMENT-QYYYY.md` - Quarterly assessments

**Refactorings:**
- `SYSTEM-REFACTORING-YYYY-MM.md` - Dated refactor records
- `FEATURE-MIGRATION.md` - Migration documentation
- `BREAKING-CHANGES-vX.md` - Breaking change records

## How to Archive

### Step 1: Prepare the File

Before moving, ensure the file has:

1. **Archival header:**
```markdown
# Feature Implementation Summary

**Status**: Archived - Implementation Complete  
**Completion Date**: 2026-02-10  
**Archived**: 2026-02-15  
**Related Active Documentation**: [Feature Guide](/docs/specifications/feature.md)
```

2. **Context for future readers:**
```markdown
## Archive Context

This document summarizes the implementation of Feature X completed in February 2026.
The feature is now part of the stable release and documented in the active specification.

For current documentation, see:
- [Feature Specification](/docs/specifications/feature.md)
- [Feature Guide](/docs/guides/FEATURE-GUIDE.md)
```

### Step 2: Move the File

```bash
# From repository root
mv docs/FEATURE-IMPLEMENTATION.md docs/archive/implementations/

# Or for categorization
mv docs/FEATURE-SUMMARY.md docs/archive/implementations/FEATURE-IMPLEMENTATION.md
```

### Step 3: Update Active Documentation

Update the main specification/guide to reflect current state:

```markdown
# Feature Specification

**Version**: 2.0.0  
**Last Updated**: 2026-02-15  
**Status**: Stable

[Current documentation...]

## Version History

### v2.0.0 (2026-02-10)
- Feature implementation complete
- See [implementation details](/docs/archive/implementations/FEATURE-IMPLEMENTATION.md)
```

### Step 4: Update Cross-References

Check for links to the archived file:

```bash
# Find references
grep -r "FEATURE-IMPLEMENTATION" docs/ --include="*.md"

# Update links to point to archive location
```

### Step 5: Update Documentation Index

Add to archive index if one exists:

```markdown
## Recent Implementations (2026)

### February 2026
- [Feature X Implementation](archive/implementations/FEATURE-IMPLEMENTATION.md)
- [System Refactoring](archive/refactorings/SYSTEM-REFACTORING-2026-02.md)
```

## Linking from Active Docs

### Reference in Version History

```markdown
## Version History

### v2.0.0 (2026-02-10)
- Complete system redesign
- **Implementation details**: [FEATURE-IMPLEMENTATION.md](/docs/archive/implementations/FEATURE-IMPLEMENTATION.md)
```

### Reference in Related Documentation

```markdown
## Related Documentation

### Active
- [Feature Guide](/docs/guides/FEATURE-GUIDE.md)
- [Component Reference](/docs/references/COMPONENT-REFERENCE.md)

### Historical
- [v1.0 Migration Guide](/docs/archive/implementations/FEATURE-v1.0-MIGRATION.md)
- [Initial Implementation](/docs/archive/implementations/FEATURE-INITIAL-IMPLEMENTATION.md)
```

### Reference in Specifications

```markdown
## Migration from v1.0

For details on the v1.0 to v2.0 migration process, see:
[v1.0 Migration Guide](/docs/archive/implementations/FEATURE-v1.0-MIGRATION.md)
```

## Best Practices

### Do Archive

✅ **Implementation summaries** - After feature completion
✅ **Version-specific guides** - When new version is released
✅ **Migration documentation** - After migration is complete
✅ **Audit reports** - After issues are addressed
✅ **Refactoring plans** - After refactoring is complete
✅ **Completed project docs** - After project closure

### Don't Archive

❌ **Active specifications** - Keep updated instead
❌ **Current guides** - Update with new information
❌ **Quick references** - Update for new versions
❌ **System documentation** - Evolve in place
❌ **Incomplete work** - Only archive completed work

### Archival Timing

**Immediate archival:**
- Audit reports (after review)
- Completed implementations (after merge)
- Project completion docs (at project close)

**Delayed archival:**
- Migration guides (keep active until migration complete)
- Deprecation notices (keep until feature removed)
- Refactoring plans (keep until refactor complete)

### Preservation Guidelines

**When archiving:**
1. Don't modify content (preserve historical accuracy)
2. Add archival metadata at the top
3. Link to current active documentation
4. Maintain original file structure
5. Keep all code examples intact

**Example archival header:**
```markdown
# Feature Implementation Summary

> **⚠️ ARCHIVED DOCUMENT**  
> **Completion Date**: 2026-02-10  
> **Archived**: 2026-02-15  
> **Status**: Implementation complete, feature is now stable  
> **Current Documentation**: [Feature Specification](/docs/specifications/feature.md)

[Original content preserved below...]
```

### Validation

After archiving, run validation scripts:

```bash
# Verify structure
./.github/skills/documentation-manager-agent/scripts/validate-doc-structure.sh

# Check for broken links
./.github/skills/documentation-manager-agent/scripts/validate-doc-links.sh docs/

# Verify no redundancy in active docs
./.github/skills/documentation-manager-agent/scripts/detect-doc-redundancy.sh
```

## Common Archival Scenarios

### Scenario 1: Feature Implementation Complete

**Before:**
```
docs/
  FEATURE-IMPLEMENTATION.md
  specifications/feature.md
```

**After:**
```
docs/
  specifications/feature.md (updated with v2.0)
  archive/implementations/
    FEATURE-IMPLEMENTATION.md (archived with header)
```

### Scenario 2: Major Version Release

**Before:**
```
docs/
  WORKFLOWS-v1.0-GUIDE.md
  WORKFLOWS-v2.0-GUIDE.md
```

**After:**
```
docs/
  specifications/workflows.md (v2.0 content)
  archive/implementations/
    WORKFLOWS-v1.0-MIGRATION.md (archived v1 → v2 migration)
```

### Scenario 3: Audit Complete

**Before:**
```
docs/
  AGENT-QUALITY-AUDIT-REPORT.md
  specifications/architecture.md
```

**After:**
```
docs/
  specifications/architecture.md (updated based on audit)
  archive/audits/
    AGENT-QUALITY-AUDIT-2026-02.md (preserved for historical record)
```

### Scenario 4: Refactoring Done

**Before:**
```
docs/
  SDK-MIGRATION-PLAN.md
  SDK-MIGRATION-PROGRESS.md
  specifications/architecture.md
```

**After:**
```
docs/
  specifications/architecture.md (updated with new structure)
  archive/refactorings/
    SDK-MIGRATION-2026-02.md (consolidated plan + progress)
```

## Checklist

Before archiving a document:

- [ ] Implementation/work is complete
- [ ] Active documentation is updated
- [ ] Archival header added to file
- [ ] Link to current docs included
- [ ] File moved to appropriate archive subdirectory
- [ ] Cross-references updated
- [ ] Documentation index updated
- [ ] Validation scripts pass
- [ ] No duplicate content in active docs

## Related Documentation

- [Documentation Guide](DOCUMENTATION-GUIDE.md) - Overall standards
- `.github/instructions/docs.instructions.md` - Core principles
- `/docs/specifications/architecture.md` - System organization

**Version**: 2.0.0  
**Last Updated**: 2026-03-07
