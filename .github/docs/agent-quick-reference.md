# Agent Quick Reference

**Last Updated**: 2026-03-07  
**Audience**: AI agents and contributors working with BusinessInfinity

---

## Repository at a Glance

| Concern | Where |
|---------|-------|
| Business workflows | `src/business_infinity/workflows.py` |
| Azure Functions entry point | `function_app.py` |
| Tests | `tests/test_workflows.py` |
| Repository spec | `.github/specs/repository.md` |
| Workflow spec | `.github/specs/workflows.md` |
| Enterprise capabilities | `.github/specs/enterprise-capabilities.md` |

---

## Run Tests

```bash
pip install -e ".[dev]"
pytest tests/ -v                          # all tests
pytest tests/ -v -k "test_name"           # targeted test
pylint src/business_infinity/             # lint
```

---

## Add a New Workflow

```python
# 1. Add to src/business_infinity/workflows.py
@app.workflow("my-workflow")
async def my_workflow(request: WorkflowRequest) -> Dict[str, Any]:
    agents = await select_c_suite_agents(request.client)
    status = await request.client.start_orchestration(
        agent_ids=[a.agent_id for a in agents],
        purpose="Describe the perpetual goal",
        context=request.body,
    )
    return {"orchestration_id": status.orchestration_id, "status": status.status.value}

# 2. Run tests
pytest tests/ -v

# 3. Update test_workflow_count if needed
```

→ **Workflow spec**: `.github/specs/workflows.md`

---

## Workflow Selection Quick Reference

| Workflow type | `workflow=` param | Use case |
|--------------|------------------|---------|
| Perpetual (default) | *(omit)* | Strategic / cross-functional |
| Hierarchical | `"hierarchical"` | One lead agent + coordinators |
| Sequential | `"sequential"` | Ordered approval chains |

---

## C-Suite Agent Selection

```python
# Preferred: explicit IDs
by_id = {a.agent_id: a for a in all_agents}
selected = [by_id[aid] for aid in C_SUITE_AGENT_IDS if aid in by_id]

# Fallback: type-based
if not selected:
    selected = [a for a in all_agents if a.agent_type in C_SUITE_TYPES]

if not selected:
    raise ValueError("No matching agents available in the catalog")
```

→ **C-suite pattern**: `.github/specs/workflows.md`

---

## Agent Quality Commands

```bash
./.github/skills/agent-evolution-agent/scripts/audit-agent-quality.sh
./.github/skills/agent-evolution-agent/scripts/detect-duplication.sh
./.github/skills/agent-evolution-agent/scripts/recommend-improvements.sh
```

---

## Key Specs Quick Links

| What | Where |
|------|-------|
| Repository role & design principles | `.github/specs/repository.md` |
| Business workflow patterns | `.github/specs/workflows.md` |
| Enterprise capability patterns | `.github/specs/enterprise-capabilities.md` |
| Agent file conventions | `.github/specs/agents.md` |
| Prompt file conventions | `.github/specs/prompts.md` |
| Skill file conventions | `.github/specs/skills.md` |
| Instruction file conventions | `.github/specs/instructions.md` |
| SDD methodology | `.github/specs/spec-driven-development.md` |
