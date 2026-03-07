# Agent Contribution Guide

**Last Updated**: 2026-03-07  
**Audience**: Contributors adding or modifying agent system files

This guide explains how to propose and implement changes to the GitHub Copilot agent intelligence system files in `.github/`.

---

## Contribution Types

### 1. New Agent File (`.github/agents/`)

Follow `.github/specs/agents.md` for required format and fields.

**Checklist**:
- [ ] YAML frontmatter valid (`name`, `description`, `prompt`, `tools`)
- [ ] `name` matches file stem in kebab-case
- [ ] `description` is 1–256 characters
- [ ] `prompt` covers: role, responsibilities, triggers, workflows, validation scripts, related docs
- [ ] Corresponding prompt file at `.github/prompts/<name>.prompt.md` (if applicable)
- [ ] Corresponding skill at `.github/skills/<name>/SKILL.md` (if applicable)

→ **Agent spec**: `.github/specs/agents.md`

### 2. New Prompt File (`.github/prompts/`)

Follow `.github/specs/prompts.md` for required format and fields.

**Checklist**:
- [ ] YAML frontmatter valid (`description`, `name`, `agent`, `model`, `tools`)
- [ ] `name` is snake_case
- [ ] Body follows section order: role → responsibilities → when to use → workflows → tools → docs
- [ ] No duplication with `copilot-instructions.md`

→ **Prompt spec**: `.github/specs/prompts.md`

### 3. New Skill File (`.github/skills/<name>/SKILL.md`)

Follow `.github/specs/skills.md` for required format and fields.

**Checklist**:
- [ ] YAML frontmatter valid (all required fields)
- [ ] `name` matches directory name in kebab-case
- [ ] Scripts in `scripts/` are executable and exit correctly
- [ ] Detailed content offloaded to `references/`

→ **Skill spec**: `.github/specs/skills.md`

### 4. New Instruction File (`.github/instructions/`)

Follow `.github/specs/instructions.md` for required format and `applyTo` patterns.

**Checklist**:
- [ ] YAML frontmatter with `applyTo` and `description`
- [ ] `applyTo` glob pattern is specific and does not overlap
- [ ] Content references specs/docs, does not duplicate them

→ **Instructions spec**: `.github/specs/instructions.md`

---

## Review Criteria

Changes to agent system files are reviewed against:

1. **Spec coverage** — does the file reference relevant `.github/specs/` files?
2. **Zero duplication** — no content repeated from other files
3. **Correct structure** — follows the required format for its file type
4. **Broken references** — all linked paths must exist

Run quality checks before submitting:

```bash
./.github/skills/agent-evolution-agent/scripts/audit-agent-quality.sh
./.github/skills/agent-evolution-agent/scripts/detect-duplication.sh
```

---

## Pull Request Template

For changes to agent system files, include in your PR description:

```
## Agent System Change

**Type**: [ ] New agent  [ ] Modified agent  [ ] New prompt  [ ] New skill  [ ] New instruction

**Spec compliance**: All required spec files referenced  ✅ / ❌
**Duplication check**: detect-duplication.sh passed  ✅ / ❌
**YAML valid**: Frontmatter parses without errors  ✅ / ❌
```

---

## Related Documentation

→ **Agent spec**: `.github/specs/agents.md`  
→ **Prompt spec**: `.github/specs/prompts.md`  
→ **Skill spec**: `.github/specs/skills.md`  
→ **Instructions spec**: `.github/specs/instructions.md`  
→ **Framework**: `.github/specs/agent-intelligence-framework.md`  
→ **Dogfooding guide**: `.github/docs/dogfooding-guide.md`
