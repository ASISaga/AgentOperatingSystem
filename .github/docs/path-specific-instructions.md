# Path-Specific Instructions Mechanism

**Last Updated**: 2026-02-14  
**Audience**: Developers, Agent System Architects

## Overview

This document explains how GitHub Copilot's path-specific instruction mechanism works, allowing coding standards to be automatically loaded based on file patterns being edited.

## How It Works

### Automatic Activation

GitHub Copilot automatically loads instruction files when you edit files matching their `applyTo` glob patterns. This happens **transparently** - no manual action required.

**Example flow:**
1. Developer opens `_sass/components/button.scss`
2. GitHub Copilot sees `.github/instructions/scss.instructions.md` with `applyTo: "**/*.{scss,sass,css},_sass/**,assets/css/**"`
3. Pattern matches → Instructions automatically loaded into context
4. Developer gets SCSS-specific guidance while editing

### Glob Pattern Frontmatter

Each instruction file must have YAML frontmatter with `applyTo` pattern:

```yaml
---
applyTo: "glob/pattern/**"
description: "Brief description for agent discovery"
---
```

**Pattern syntax:**
- `**/*.ext` - All files with extension, any depth
- `path/**` - All files under path
- `*.{ext1,ext2}` - Multiple extensions
- `**/*.{ext1,ext2},path/**` - Multiple patterns (comma-separated)

### Current Instruction Files

| File | applyTo Pattern | Loads When Editing |
|------|-----------------|-------------------|
| `python.instructions.md` | `**/*.py` | Any Python file |
| `azure-functions.instructions.md` | `src/**/*.py,function_app.py,tests/**/*.py` | Azure Functions / workflow files |
| `docs.instructions.md` | `docs/**/*.md,*.md` | Documentation files |
| `agents.instructions.md` | `.github/agents/*.agent.md` | Agent definition files |
| `prompts.instructions.md` | `.github/prompts/*.prompt.md` | Prompt files |
| `skills.instructions.md` | `.github/skills/*/SKILL.md` | Skill files |
| `github-specs.instructions.md` | `.github/specs/*.md` | Specification files |
| `github-docs.instructions.md` | `.github/docs/*.md` | Agent doc files |
| `github-instructions.instructions.md` | `.github/instructions/*.md` | Instruction files |

## Benefits

### 1. Context Window Efficiency

**Without path-specific instructions:**
- All guidance loaded all the time
- Irrelevant information consumes context
- Generic advice dilutes specific guidance

**With path-specific instructions:**
- Only relevant guidance loaded
- Context focused on current file type
- More room for detailed, specific advice

### 2. Zero Duplication

**copilot-instructions.md** provides:
- High-level architecture
- Agent system overview
- Cross-cutting concerns
- Navigation to detailed resources

**Path-specific instructions** provide:
- Language/framework-specific patterns
- Tool integration (npm scripts, linters)
- File format requirements
- Best practices for that file type

**No overlap** = Maximum context efficiency

### 3. Maintainability

**Centralized by concern:**
- All SCSS patterns in one file
- All HTML patterns in one file
- Easy to find and update

**Automatic distribution:**
- Changes apply immediately
- No manual syncing required
- Single source of truth

## Instruction File Structure

### Standard Template

```markdown
---
applyTo: "**/*.ext,path/**"
description: "Brief description for agent discovery"
---

# File Type Instructions

## File Format
[Format requirements specific to this file type]

## Coding Standards
[Language/framework-specific best practices]

## Tool Integration
\```bash
npm run relevant-command
npm run lint-command
\```

## Common Patterns
[Code examples and patterns]

## References
→ **Specification**: `.github/specs/relevant-spec.md`  
→ **Documentation**: `/docs/guides/relevant-guide.md`

---

**Applies to**: [glob pattern]  
**Version**: X.Y  
**Last Updated**: YYYY-MM-DD
```

### Content Guidelines

**DO include:**
- File format requirements
- Coding standards specific to file type
- Tool integration commands
- Quick reference patterns
- Links to detailed specs/docs

**DON'T include:**
- Content from `copilot-instructions.md` (no duplication)
- Detailed specifications (link to `.github/specs/`)
- Long tutorials (link to `.github/docs/`)
- Generic guidance (goes in `copilot-instructions.md`)

## Testing Glob Patterns

### Command Line Testing

```bash
# Enable globstar for ** patterns
shopt -s globstar

# Test your pattern
echo **/*.scss
echo .github/**/*.md
echo **/*.{html,liquid}
```

### Online Testing

Use [globtester.com](https://globtester.com) to test patterns against file lists.

### Verification Checklist

- [ ] Pattern matches intended files
- [ ] Pattern doesn't match unintended files
- [ ] No overlap with other instruction files
- [ ] Pattern is specific enough (not `**/*`)
- [ ] Pattern uses correct syntax

## Common Patterns

### File Extension Only

```yaml
applyTo: "**/*.ext"
```
Matches all `.ext` files anywhere in repository.

### Directory and Extensions

```yaml
applyTo: "**/*.ext,path/**"
```
Matches all `.ext` files PLUS all files under `path/`.

### Multiple Extensions

```yaml
applyTo: "**/*.{ext1,ext2,ext3}"
```
Matches files with any of the listed extensions.

### Complex Multi-Pattern

```yaml
applyTo: "**/*.{ext1,ext2},path1/**,path2/**/*.ext3"
```
Matches multiple patterns combined with commas.

## Best Practices

### Pattern Specificity

**Too broad** ❌
```yaml
applyTo: "**/*"  # Matches everything
```

**Too narrow** ❌
```yaml
applyTo: "_sass/components/button.scss"  # One file only
```

**Just right** ✅
```yaml
applyTo: "**/*.scss,_sass/**,assets/css/**"  # All SCSS contexts
```

### Avoid Overlap

**Problematic:**
```yaml
# File 1
applyTo: "**/*.md"

# File 2  
applyTo: "docs/**/*.md"
```
Both load for `docs/guide.md` - duplication!

**Better:**
```yaml
# File 1
applyTo: ".github/**/*.md"

# File 2
applyTo: "docs/**/*.md,*.md"
```
Clear separation by directory.

### Description Field

**Vague** ❌
```yaml
description: "Instructions for files"
```

**Clear** ✅
```yaml
description: "SCSS coding standards and ontology system"
```

## Integration with copilot-instructions.md

### Reference, Don't Duplicate

**copilot-instructions.md should:**
```markdown
## Path-Specific Instructions

Detailed coding standards are in `.github/instructions/` 
and are automatically activated by file path:

- `python.instructions.md` — Python coding standards
- `azure-functions.instructions.md` — Azure Functions / AOS workflow patterns
- `docs.instructions.md` — Documentation standards

→ **Mechanism**: `.github/docs/path-specific-instructions.md`
```

**DON'T do this:**
```markdown
## SCSS Instructions

When editing SCSS files, use the ontology system...
[500 lines of detailed SCSS guidance]

## HTML Instructions

When editing HTML files, use semantic elements...
[500 lines of detailed HTML guidance]
```
→ This defeats the purpose! Move to instruction files.

### Navigation Pattern

```
copilot-instructions.md (high-level overview)
    ↓ references
.github/instructions/*.instructions.md (path-specific details)
    ↓ references
.github/specs/*.md (detailed specifications)
    ↓ references
/docs/ (comprehensive documentation)
```

## Troubleshooting

### Instructions Not Loading

**Check:**
1. Frontmatter valid YAML syntax
2. File has `.instructions.md` extension
3. File in `.github/instructions/` directory
4. `applyTo` pattern matches file being edited
5. Pattern syntax correct (no typos)

### Too Much Context Loaded

**Problem**: Multiple instruction files loading for one file type

**Solution**: Review `applyTo` patterns for overlap, refine to be mutually exclusive

### Instructions Loading for Wrong Files

**Problem**: Pattern too broad

**Solution**: Make pattern more specific, test thoroughly

## Migration from Monolithic Instructions

### Before (Problematic)

```
.github/
└── copilot-instructions.md (5000 lines)
    ├── SCSS guidance
    ├── HTML guidance  
    ├── JavaScript guidance
    ├── Documentation standards
    └── ... (everything)
```

**Problems:**
- All loaded all the time
- Context window bloat
- Hard to maintain
- Generic and specific mixed

### After (Optimized)

```
.github/
├── copilot-instructions.md (150 lines)
│   └── High-level architecture only
└── instructions/
    ├── python.instructions.md            (auto-loads for Python)
    ├── azure-functions.instructions.md   (auto-loads for workflow files)
    └── docs.instructions.md              (auto-loads for docs)
```

**Benefits:**
- Only relevant guidance loaded
- Clear separation of concerns
- Easy to maintain each file type
- Maximum context efficiency

## Related Documentation

- **Agent Intelligence Framework**: `.github/specs/agent-intelligence-framework.md`
- **Instruction File Standards**: `.github/instructions/github-instructions.instructions.md`
- **Agent System Overview**: `.github/docs/agent-system-overview.md`

---

**Version**: 1.0.0  
**Purpose**: Document path-specific instruction mechanism for reference from copilot-instructions.md
