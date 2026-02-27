# AOS Client SDK Enhancement Requests

**From:** BusinessInfinity  
**To:** AgentOperatingSystem / aos-client-sdk  
**Date:** 2026-02-27  
**Context:** After refactoring BusinessInfinity to fully utilize the aos-client-sdk, the following enhancements would significantly improve the SDK's capabilities for real-world enterprise applications.

---

## Priority 1 — Critical for Production

### 1. Knowledge Base API in AOSClient

**Problem:** BusinessInfinity previously had a local knowledge base module (`src/knowledge/`) for managing documents, policies, decisions, and procedures. After refactoring to SDK-only, there is no SDK-level API for knowledge management.

**Requested Enhancement:**

```python
# AOSClient additions
async def create_document(self, title: str, doc_type: str, content: dict, **kwargs) -> Document
async def get_document(self, document_id: str) -> Document
async def search_documents(self, query: str, doc_type: str = None, limit: int = 10) -> List[Document]
async def update_document(self, document_id: str, content: dict) -> Document
async def delete_document(self, document_id: str) -> None
```

**Rationale:** Enterprise applications need persistent knowledge management. This should be an AOS-level service accessible through the SDK, not reimplemented in each client app.

---

### 2. Risk Registry API in AOSClient

**Problem:** BusinessInfinity had a local risk registry (`src/risk/`) for risk identification, assessment, and mitigation. After refactoring, there is no SDK-level risk management.

**Requested Enhancement:**

```python
# AOSClient additions
async def register_risk(self, risk_data: dict) -> Risk
async def assess_risk(self, risk_id: str, likelihood: float, impact: float, **kwargs) -> Risk
async def get_risks(self, status: str = None, category: str = None) -> List[Risk]
async def update_risk_status(self, risk_id: str, status: str) -> Risk
async def add_mitigation_plan(self, risk_id: str, plan: str, **kwargs) -> Risk
```

**Rationale:** Risk governance is a cross-cutting concern that applies to all AOS client applications.

---

### 3. Audit Trail / Decision Ledger API

**Problem:** BusinessInfinity had an audit trail system (`src/core/audit_trail.py`) and decision ledger (`src/orchestration/DecisionLedger.py`) for immutable logging of agent decisions. This is critical for compliance but has no SDK equivalent.

**Requested Enhancement:**

```python
# AOSClient additions
async def log_decision(self, decision: dict) -> DecisionRecord
async def get_decision_history(self, orchestration_id: str = None, agent_id: str = None) -> List[DecisionRecord]
async def get_audit_trail(self, start_time: datetime = None, end_time: datetime = None) -> List[AuditEntry]
```

**Rationale:** Immutable audit trails are required for governance, compliance, and regulatory requirements in enterprise applications.

---

### 4. Covenant Management API

**Problem:** BusinessInfinity had a covenant manager (`src/core/covenant_manager.py`) for creating, validating, and enforcing business covenants. This is essential for the Global Boardroom Network concept but has no SDK-level support.

**Requested Enhancement:**

```python
# AOSClient additions
async def create_covenant(self, covenant_data: dict) -> Covenant
async def validate_covenant(self, covenant_id: str) -> CovenantValidation
async def list_covenants(self, status: str = None) -> List[Covenant]
async def sign_covenant(self, covenant_id: str, signer: str) -> Covenant
```

**Rationale:** Covenant-based governance is a core feature of the AOS ecosystem and should be a first-class SDK concept.

---

## Priority 2 — Important for Feature Completeness

### 5. Workflow Result Callbacks

**Problem:** The current SDK creates perpetual orchestrations but provides no mechanism for the client app to receive intermediate results, status updates, or agent outputs. The Service Bus trigger only receives terminal status updates.

**Requested Enhancement:**

```python
# AOSApp additions
@app.on_orchestration_update("strategic-review")
async def handle_update(update: OrchestrationUpdate):
    """Called whenever the orchestration produces intermediate output."""
    logger.info("Agent %s produced: %s", update.agent_id, update.output)

# Or callback-based
@app.workflow("strategic-review")
async def strategic_review(request: WorkflowRequest):
    status = await request.client.start_orchestration(
        agent_ids=agent_ids,
        purpose="...",
        on_update=handle_intermediate_result,  # New parameter
    )
```

**Rationale:** Enterprise applications need real-time visibility into ongoing orchestrations, not just final status.

---

### 6. Analytics and Metrics API

**Problem:** BusinessInfinity had analytics modules (`src/analytics/`) for KPI tracking, business metrics, and performance monitoring. The SDK provides no analytics primitives.

**Requested Enhancement:**

```python
# AOSClient additions
async def record_metric(self, name: str, value: float, tags: dict = None) -> None
async def get_metrics(self, name: str, start: datetime = None, end: datetime = None) -> MetricsSeries
async def create_kpi(self, kpi_definition: dict) -> KPI
async def get_kpi_dashboard(self) -> Dashboard
```

**Rationale:** Business applications need analytics capabilities that are consistent across the AOS ecosystem.

---

### 7. MCP Server Integration in SDK

**Problem:** BusinessInfinity had MCP server configurations (`src/mcp/`) for integrating with ERPNext, LinkedIn, Reddit, and other services via Model Context Protocol. The SDK has no MCP support.

**Requested Enhancement:**

```python
# AOSClient additions
async def list_mcp_servers(self) -> List[MCPServer]
async def call_mcp_tool(self, server: str, tool: str, args: dict) -> Any
async def get_mcp_server_status(self, server: str) -> MCPServerStatus

# Or decorator-based for direct MCP integration
@app.mcp_tool("erp-search")
async def erp_search(request: MCPToolRequest):
    return await request.client.call_mcp_tool("erpnext", "search", request.args)
```

**Rationale:** MCP is a key integration pattern in the AOS ecosystem. The SDK should provide first-class MCP support.

---

### 8. Reliability Patterns in SDK

**Problem:** BusinessInfinity had reliability patterns (`src/core/reliability.py`) including CircuitBreaker, RetryPolicy, and IdempotencyHandler. These are general-purpose patterns that benefit all client apps.

**Requested Enhancement:**

```python
# aos_client.reliability module
from aos_client.reliability import CircuitBreaker, RetryPolicy, IdempotencyHandler

# Auto-applied to AOSClient calls
client = AOSClient(
    endpoint="...",
    retry_policy=RetryPolicy(max_retries=3),
    circuit_breaker=CircuitBreaker(failure_threshold=5),
)
```

**Rationale:** Reliability patterns should be built into the SDK so every client app benefits from them automatically.

---

### 9. Observability Integration

**Problem:** BusinessInfinity had observability features (`src/core/observability.py`) including structured logging, correlation context, metrics collection, and health checks. These should be SDK-level concerns.

**Requested Enhancement:**

```python
# Built into AOSApp
app = AOSApp(
    name="business-infinity",
    observability=ObservabilityConfig(
        structured_logging=True,
        correlation_tracking=True,
        metrics_endpoint="/metrics",
        health_checks=["aos", "service-bus"],
    ),
)

# Automatic correlation ID propagation
@app.workflow("strategic-review")
async def strategic_review(request: WorkflowRequest):
    # request.correlation_id automatically set and propagated to AOS calls
    ...
```

**Rationale:** Observability is a cross-cutting concern that should be consistent and automatic for all AOS applications.

---

## Priority 3 — Nice to Have

### 10. Agent Interaction API (Direct Messaging)

**Problem:** BusinessInfinity had an `ask_agent` pattern where users could query individual agents directly. The current SDK only supports starting orchestrations (multi-agent workflows).

**Requested Enhancement:**

```python
# AOSClient additions
async def ask_agent(self, agent_id: str, message: str, context: dict = None) -> AgentResponse
async def send_to_agent(self, agent_id: str, message: dict) -> None
```

**Rationale:** Some use cases need direct 1:1 agent interaction, not full orchestrations.

---

### 11. Workflow Templates / Composable Workflows

**Problem:** BusinessInfinity has 8 workflows that follow similar patterns (select agents → start orchestration → return status). The SDK could provide workflow composition primitives.

**Requested Enhancement:**

```python
# Workflow composition
from aos_client import workflow_template

@workflow_template
async def c_suite_orchestration(request: WorkflowRequest, agent_filter, purpose, purpose_scope):
    agents = await select_c_suite_agents(request.client)
    agent_ids = [a.agent_id for a in agents if agent_filter(a)]
    return await request.client.start_orchestration(
        agent_ids=agent_ids,
        purpose=purpose,
        purpose_scope=purpose_scope,
        context=request.body,
    )

# Reuse the template
@app.workflow("strategic-review")
async def strategic_review(request):
    return await c_suite_orchestration(request,
        agent_filter=lambda a: True,
        purpose="Drive strategic review",
        purpose_scope="C-suite strategic alignment",
    )
```

**Rationale:** Reduces code duplication across workflows and enables pattern reuse.

---

### 12. Network Discovery API

**Problem:** BusinessInfinity had network discovery (`src/network/discovery.py`) for finding peer boardrooms in the Global Boardroom Network. This should be an AOS-level service.

**Requested Enhancement:**

```python
# AOSClient additions
async def discover_peers(self, criteria: dict) -> List[PeerApp]
async def join_network(self, network_id: str) -> NetworkMembership
async def list_networks(self) -> List[Network]
```

**Rationale:** Multi-application discovery and federation should be managed at the platform level.

---

### 13. Local Development Experience

**Problem:** The SDK requires AOS and RealmOfAgents to be running for any functionality. For local development, a mock/stub mode would be valuable.

**Requested Enhancement:**

```python
# Local development mode with built-in mocks
app = AOSApp(name="business-infinity", mode="local")

# Or explicit mock client
from aos_client.testing import MockAOSClient

client = MockAOSClient()
client.add_agent(AgentDescriptor(agent_id="ceo", agent_type="LeadershipAgent", ...))
```

**Rationale:** Developers should be able to develop and test workflows without running the full AOS infrastructure locally.

---

### 14. Publish aos-client-sdk to PyPI

**Problem:** The SDK currently exists only as source code in the AOS meta-repository under `docs/agent-repositories/aos-client-sdk/`. It is not published to PyPI, requiring local installation.

**Requested Enhancement:** Publish `aos-client-sdk` to PyPI so client apps can declare a simple pip dependency.

**Rationale:** All AOS client apps (BusinessInfinity, future apps) need the SDK. A PyPI package is the standard Python distribution mechanism.

---

## Summary

| # | Enhancement | Priority | Impact |
|---|-------------|----------|--------|
| 1 | Knowledge Base API | P1 | Enables persistent knowledge management |
| 2 | Risk Registry API | P1 | Enables enterprise risk governance |
| 3 | Audit Trail / Decision Ledger | P1 | Required for compliance |
| 4 | Covenant Management API | P1 | Core AOS governance feature |
| 5 | Workflow Result Callbacks | P2 | Real-time orchestration visibility |
| 6 | Analytics and Metrics API | P2 | Business intelligence capabilities |
| 7 | MCP Server Integration | P2 | Tool/service integration pattern |
| 8 | Reliability Patterns | P2 | Automatic resilience for all apps |
| 9 | Observability Integration | P2 | Consistent monitoring/tracing |
| 10 | Agent Interaction API | P3 | Direct 1:1 agent messaging |
| 11 | Workflow Templates | P3 | Code reuse across workflows |
| 12 | Network Discovery API | P3 | Multi-app federation |
| 13 | Local Development Mocks | P3 | Developer experience |
| 14 | PyPI Publication | P3 | Standard package distribution |

---

*This document was generated during the BusinessInfinity v3.0 refactoring to the aos-client-sdk. Each enhancement represents a capability that was previously implemented locally in BusinessInfinity but should be elevated to the AOS platform for reuse across all client applications.*
