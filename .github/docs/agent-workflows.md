# Agent Workflow Guide

**Last Updated**: 2026-03-07  
**Audience**: AI agents and contributors working with BusinessInfinity

Practical workflows for common tasks in the BusinessInfinity repository.

---

## Workflow 1: Adding a Business Workflow

**Trigger**: New business process needs to be orchestrated via C-suite agents.

### Steps

1. **Read the workflow spec** to understand patterns:
   ```bash
   # Reference: .github/specs/workflows.md
   ```

2. **Add `@app.workflow` decorator** in `src/business_infinity/workflows.py`:
   ```python
   @app.workflow("my-workflow")
   async def my_workflow(request: WorkflowRequest) -> Dict[str, Any]:
       agents = await select_c_suite_agents(request.client)
       agent_ids = [a.agent_id for a in agents if agent_filter(a)]
       if not agent_ids:
           raise ValueError("No matching agents available in the catalog")
       status = await request.client.start_orchestration(
           agent_ids=agent_ids,
           purpose="Perpetual goal description",
           purpose_scope="Scope of agent responsibility",
           context=request.body,
       )
       return {"orchestration_id": status.orchestration_id, "status": status.status.value}
   ```

3. **Run tests** to validate:
   ```bash
   pytest tests/ -v
   pylint src/business_infinity/workflows.py
   ```

4. **Update `test_workflow_count`** in `tests/test_workflows.py` if needed.

→ **Workflow patterns**: `.github/specs/workflows.md`

---

## Workflow 2: Adding an Enterprise Capability

**Trigger**: New capability (knowledge search, risk, MCP tool, etc.) is needed.

### Steps

1. **Read the enterprise capabilities spec**:
   ```bash
   # Reference: .github/specs/enterprise-capabilities.md
   ```

2. **Add the workflow** following the relevant pattern (knowledge, risk, MCP, etc.)

3. **Register MCP tools if applicable**:
   ```python
   @app.mcp_tool("tool-name")
   async def my_tool(request) -> Any:
       return await request.client.call_mcp_tool("server", "method", request.body)
   ```

4. **Run tests and lint**:
   ```bash
   pytest tests/ -v && pylint src/
   ```

→ **Enterprise patterns**: `.github/specs/enterprise-capabilities.md`

---

## Workflow 3: Creating a Feature Specification (SDD)

**Trigger**: New feature needs structured specification before implementation.

### Steps

1. **Invoke Spec Manager Agent**:
   - Triggers `spec-create.prompt.md` → `spec-plan.prompt.md` → `spec-tasks.prompt.md`

2. **Create feature branch and spec**:
   ```bash
   ./.github/skills/spec-manager/scripts/create-feature-branch.sh "<description>"
   ```

3. **Validate spec completeness**:
   ```bash
   ./.github/skills/spec-manager/scripts/validate-spec.sh specs/<NNN>-<slug>/spec.md
   ```

→ **SDD methodology**: `.github/docs/spec-driven.md`  
→ **SDD spec**: `.github/specs/spec-driven-development.md`

---

## Workflow 4: Agent Quality Audit (Dogfooding)

**Trigger**: Weekly or after making agent/skill/prompt changes.

### Steps

```bash
# 1. Full quality audit
./.github/skills/agent-evolution-agent/scripts/audit-agent-quality.sh

# 2. Check spec references
./.github/skills/agent-evolution-agent/scripts/sync-agents-with-specs.sh

# 3. Detect duplication
./.github/skills/agent-evolution-agent/scripts/detect-duplication.sh

# 4. Get recommendations
./.github/skills/agent-evolution-agent/scripts/recommend-improvements.sh

# 5. Track metrics over time
./.github/skills/agent-evolution-agent/scripts/track-metrics.sh
```

→ **Dogfooding guide**: `.github/docs/dogfooding-guide.md`

---

## Workflow 5: Documentation Quality Check

**Trigger**: Before committing documentation changes.

```bash
# Structure validation
./.github/skills/documentation-manager-agent/scripts/validate-doc-structure.sh

# Link validation
./.github/skills/documentation-manager-agent/scripts/validate-doc-links.sh docs/

# Redundancy detection
./.github/skills/documentation-manager-agent/scripts/detect-doc-redundancy.sh

# Metadata validation
./.github/skills/documentation-manager-agent/scripts/check-doc-metadata.sh docs/
```

---

## Key References

- `.github/specs/repository.md` — Repository design principles
- `.github/specs/workflows.md` — Business workflow patterns
- `.github/specs/enterprise-capabilities.md` — Enterprise capability patterns
- `.github/docs/conventional-tools.md` — All tool commands
- `.github/docs/dogfooding-guide.md` — Agent quality workflows
