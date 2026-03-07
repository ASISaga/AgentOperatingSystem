# Decision Matrices

**Last Updated**: 2026-03-07  
**Audience**: AI agents and contributors

Quick-reference decision trees for common scenarios in BusinessInfinity.

## "Should I add a new workflow?"

| Scenario | Action |
|----------|--------|
| New business process needs orchestration | ✅ Add `@app.workflow` in `workflows.py` |
| Infrastructure concern (auth, messaging) | ❌ Belongs in `aos-client-sdk`, not here |
| Agent internal logic | ❌ Belongs in `RealmOfAgents`, not here |
| Existing workflow needs variation | ⚠️ Check if `c_suite_orchestration` template fits first |

→ **Design principles**: `.github/specs/repository.md`

---

## "Which workflow variant should I use?"

| Goal | Variant | `workflow=` param |
|------|---------|-------------------|
| Continuous strategic alignment | Perpetual | *(omit)* |
| Analysis led by one agent | Hierarchical | `"hierarchical"` |
| Ordered approval (CEO → CFO) | Sequential | `"sequential"` |

→ **Workflow variants**: `.github/specs/workflows.md`

---

## "Which agents should I select?"

| Workflow type | Selection strategy |
|--------------|-------------------|
| All C-suite | `agent_filter=lambda a: True` |
| Finance-focused | Filter by `agent_id in ["ceo", "cfo"]` |
| Market-focused | Filter `CMOAgent` + CEO fallback |
| Single agent type | Filter by `agent_type` |

**Rule**: Always prefer `agent_id` matching. Fall back to `agent_type` only when no IDs found. Raise `ValueError` when nothing matched.

→ **C-suite selection pattern**: `.github/specs/workflows.md`

---

## "Should I create a spec before implementing?"

| Scenario | Action |
|----------|--------|
| New feature with unclear requirements | ✅ Use SDD: Specify → Plan → Tasks |
| Simple workflow addition with clear pattern | ✅ Check existing spec in `.github/specs/workflows.md` |
| Bug fix | ❌ Implement directly, no spec needed |
| Refactoring | ⚠️ Use spec if architectural changes; otherwise proceed |

→ **SDD workflow**: `.github/specs/spec-driven-development.md`

---

## "Should I modify the agent intelligence system files?"

| Scenario | Action |
|----------|--------|
| New agent file needed | ✅ Follow `.github/specs/agents.md` |
| New prompt file needed | ✅ Follow `.github/specs/prompts.md` |
| New skill file needed | ✅ Follow `.github/specs/skills.md` |
| New instruction file needed | ✅ Follow `.github/specs/instructions.md` |
| Content belongs in a spec | ✅ Add to `.github/specs/` |
| Content belongs in a guide | ✅ Add to `.github/docs/` |
| Duplicating existing content | ❌ Reference the source, don't duplicate |

---

## "Where does this content belong?"

| Content type | Location |
|-------------|---------|
| Business workflow code | `src/business_infinity/workflows.py` |
| Repository role & tech stack | `.github/specs/repository.md` |
| Workflow patterns & specs | `.github/specs/workflows.md` |
| Agent file conventions | `.github/specs/agents.md` |
| Prompt file conventions | `.github/specs/prompts.md` |
| Skill file conventions | `.github/specs/skills.md` |
| Path-specific coding standards | `.github/instructions/*.instructions.md` |
| Implementation guides & how-tos | `.github/docs/` |
| Feature specifications | `specs/<NNN>-<slug>/spec.md` |
