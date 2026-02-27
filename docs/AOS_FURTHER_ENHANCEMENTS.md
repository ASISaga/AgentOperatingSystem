AOS Client SDK — Further Enhancement Requests
From: BusinessInfinity
To: AgentOperatingSystem / aos-client-sdk
Date: 2026-02-27
Context: After integrating all 14 enhancements from SDK v4.0.0 into BusinessInfinity, we've identified additional improvements that would further strengthen the enterprise experience. These are informed by exercising the v4.0.0 APIs in production-style workflows.

Priority 1 — Critical for Production Readiness
1. Knowledge Base CRUD Completeness
Problem: The SDK provides create_document, get_document, search_documents, update_document, and delete_document. However, BusinessInfinity needs batch operations and versioned document support.

Requested Enhancement:

# AOSClient additions
async def create_documents_batch(self, documents: List[dict]) -> List[Document]
async def get_document_versions(self, document_id: str) -> List[Document]
async def restore_document_version(self, document_id: str, version: int) -> Document
async def export_documents(self, query: str, format: str = "json") -> bytes
Rationale: Enterprise knowledge management requires bulk operations for onboarding (importing existing policies) and version history for compliance audits. The boardroom creates many decisions simultaneously that should be batched.

2. Risk Registry — Aggregation and Heatmaps
Problem: The SDK provides individual risk CRUD and assessment, but BusinessInfinity's risk-assessment orchestration needs aggregate risk views (risk heatmaps, category summaries) to inform C-suite decision-making.

Requested Enhancement:

# AOSClient additions
async def get_risk_heatmap(self, category: str = None) -> RiskHeatmap
async def get_risk_summary(self, category: str = None) -> RiskSummary
async def get_risk_trends(self, period: str = "30d") -> List[RiskTrend]
# New models
class RiskHeatmap(BaseModel):
    cells: List[RiskHeatmapCell]  # likelihood x impact grid
    total_risks: int

class RiskSummary(BaseModel):
    by_category: Dict[str, int]
    by_severity: Dict[str, int]
    by_status: Dict[str, int]
    total_open: int

class RiskTrend(BaseModel):
    period: str
    new_risks: int
    mitigated_risks: int
    risk_score_avg: float
Rationale: Aggregate risk data drives the boardroom's strategic decisions. Without it, each workflow must fetch all risks and compute aggregates client-side, which is inefficient and inconsistent.

3. Covenant Lifecycle Events
Problem: The covenant management API allows create/validate/sign/list, but BusinessInfinity's covenant-compliance orchestration needs to be notified when covenants are violated, expired, or amended by other parties. There is no event-driven covenant lifecycle.

Requested Enhancement:

# AOSApp additions
@app.on_covenant_event("violated")
async def handle_covenant_violation(event: CovenantEvent) -> None:
    """Triggered when a covenant is violated."""
    ...

@app.on_covenant_event("expiring")
async def handle_covenant_expiring(event: CovenantEvent) -> None:
    """Triggered when a covenant is nearing expiration."""
    ...

# New model
class CovenantEvent(BaseModel):
    covenant_id: str
    event_type: str  # violated, expiring, amended, revoked
    details: Dict[str, Any]
    timestamp: datetime
Rationale: Compliance monitoring cannot be effective if it must poll. Event-driven covenant lifecycle notifications enable proactive governance.

4. Audit Trail — Compliance Reporting
Problem: The audit trail API provides log_decision and get_decision_history, but BusinessInfinity needs structured compliance reports (e.g., "all decisions in Q1 2026 with their rationale and signoff chain") for regulatory submissions.

Requested Enhancement:

# AOSClient additions
async def generate_compliance_report(
    self,
    start_time: datetime,
    end_time: datetime,
    report_type: str = "decisions",
    format: str = "json",
) -> ComplianceReport

async def get_decision_chain(
    self,
    decision_id: str,
) -> DecisionChain

# New models
class ComplianceReport(BaseModel):
    report_type: str
    period_start: datetime
    period_end: datetime
    entries: List[DecisionRecord]
    summary: Dict[str, Any]
    generated_at: datetime

class DecisionChain(BaseModel):
    decision_id: str
    chain: List[DecisionRecord]  # decision → rationale → approvals
    complete: bool
Rationale: Regulatory compliance requires structured reporting, not just raw log access. Building reports client-side from raw audit entries is error-prone and inconsistent across apps.

Priority 2 — Important for Feature Completeness
5. Workflow Orchestration Status Streaming
Problem: @app.on_orchestration_update receives updates, but there is no SDK mechanism for the client to subscribe to a specific orchestration's update stream. The update handler is registered globally per workflow name. BusinessInfinity's boardroom session needs to track updates from a specific orchestration instance.

Requested Enhancement:

# AOSClient additions
async def subscribe_to_orchestration(
    self,
    orchestration_id: str,
    callback: Callable[[OrchestrationUpdate], Awaitable[None]],
) -> Subscription

# Or async iterator pattern
async for update in client.stream_orchestration_updates(orchestration_id):
    process(update)
Rationale: Per-instance streaming enables rich UIs and detailed monitoring dashboards that show real-time agent activity within a specific boardroom session.

6. Multi-Tenant Support
Problem: BusinessInfinity will eventually serve multiple organizations (Global Boardroom Network). The SDK's AOSClient is single-endpoint. There is no tenant isolation or multi-endpoint routing.

Requested Enhancement:

# AOSClient additions
client = AOSClient(
    endpoint="...",
    tenant_id="org-123",  # Tenant isolation
)

# Or multi-tenant factory
from aos_client import AOSMultiTenantClient

client = AOSMultiTenantClient(
    endpoints={"org-123": "https://...", "org-456": "https://..."},
)
agents = await client.for_tenant("org-123").list_agents()
Rationale: The Global Boardroom Network concept requires federated multi-tenant operation. Without SDK support, each client must manage tenant routing manually.

7. Analytics — Custom Dashboards and Alerts
Problem: The analytics API provides basic record_metric / get_metrics / create_kpi / get_kpi_dashboard. BusinessInfinity needs custom dashboards per workflow and threshold-based alerts (e.g., "alert when risk score exceeds 8.0").

Requested Enhancement:

# AOSClient additions
async def create_dashboard(self, name: str, kpi_ids: List[str], layout: dict = None) -> Dashboard
async def create_alert(self, metric_name: str, threshold: float, condition: str = "gt") -> Alert
async def list_alerts(self, status: str = None) -> List[Alert]

# New model
class Alert(BaseModel):
    id: str
    metric_name: str
    threshold: float
    condition: str  # gt, lt, eq
    status: str  # active, triggered, silenced
    last_triggered: Optional[datetime]
Rationale: Enterprise applications need proactive monitoring, not just passive metric collection.

8. MCP Tool — Bidirectional Communication
Problem: The MCP integration is currently request/response (call_mcp_tool). BusinessInfinity needs MCP servers to push notifications to the app (e.g., ERP webhook events, LinkedIn notifications).

Requested Enhancement:

# AOSApp additions
@app.on_mcp_event("erpnext", "order_created")
async def handle_erp_order(event: MCPEvent) -> None:
    """Triggered when ERPNext creates a new order."""
    ...

# New model
class MCPEvent(BaseModel):
    server: str
    event_type: str
    payload: Dict[str, Any]
    timestamp: datetime
Rationale: Real-world enterprise integrations are event-driven. The boardroom should react to ERP events, not just poll.

9. Network Discovery — Covenant-Based Federation
Problem: The network discovery API (discover_peers, join_network, list_networks) is basic. The Global Boardroom Network concept requires covenant-based peer authentication — peers must sign a covenant before joining the network.

Requested Enhancement:

# AOSClient additions
async def create_network(
    self,
    name: str,
    covenant_id: str,  # Required covenant for membership
    description: str = "",
) -> Network

async def request_membership(
    self,
    network_id: str,
    covenant_signature: str,
) -> NetworkMembership

async def verify_peer(
    self,
    peer_app_id: str,
    network_id: str,
) -> PeerVerification
Rationale: Federated networks need trust guarantees. Covenant-based federation ensures all peers adhere to shared governance standards.

Priority 3 — Nice to Have
10. SDK CLI Tool
Problem: All SDK operations require writing Python code. For quick operations (register app, check health, list agents, deploy), a CLI tool would improve developer experience.

Requested Enhancement:

# CLI examples
aos register --app business-infinity --workflows strategic-review,market-analysis
aos health --endpoint https://my-aos.azurewebsites.net
aos agents list
aos deploy --app business-infinity --resource-group rg-bi
Rationale: CLI tools reduce the barrier to entry and speed up common operations.

11. Workflow Versioning and A/B Testing
Problem: When BusinessInfinity updates a workflow (e.g., changing the agent selection for strategic review), there's no way to run both versions simultaneously for comparison.

Requested Enhancement:

@app.workflow("strategic-review", version="2.0")
async def strategic_review_v2(request: WorkflowRequest):
    ...

# Traffic splitting
app.set_traffic_split("strategic-review", {"1.0": 50, "2.0": 50})
Rationale: Enterprise applications need safe rollout mechanisms for workflow changes.

12. Webhook Support for External Systems
Problem: BusinessInfinity needs to notify external systems (Slack, Teams, email) when orchestrations produce significant outputs. The SDK has no outbound webhook mechanism.

Requested Enhancement:

# AOSApp additions
@app.webhook("slack-notifications")
async def notify_slack(event: WebhookEvent) -> None:
    """Send notification to Slack when a decision is made."""
    ...

# AOSClient additions
async def register_webhook(self, url: str, events: List[str]) -> Webhook
async def list_webhooks(self) -> List[Webhook]
Rationale: Enterprise workflows must integrate with existing communication and notification systems.

Summary
#	Enhancement	Priority	Impact
1	Knowledge Base Batch & Versioning	P1	Bulk operations, compliance
2	Risk Heatmaps & Aggregation	P1	Strategic risk visibility
3	Covenant Lifecycle Events	P1	Proactive compliance monitoring
4	Audit Trail Compliance Reports	P1	Regulatory reporting
5	Orchestration Status Streaming	P2	Real-time monitoring
6	Multi-Tenant Support	P2	Global Boardroom Network
7	Analytics Dashboards & Alerts	P2	Proactive monitoring
8	MCP Bidirectional Events	P2	Event-driven integrations
9	Covenant-Based Federation	P2	Trusted peer networks
10	SDK CLI Tool	P3	Developer experience
11	Workflow Versioning & A/B	P3	Safe rollout
12	Webhook Support	P3	External notifications
This document captures enhancement requests that emerged after integrating AOS Client SDK v4.0.0 into BusinessInfinity v4.0.0. Each enhancement represents a production-readiness gap or strategic capability that would benefit all AOS client applications.
