"""BusinessInfinity workflows — purpose-driven perpetual orchestrations.

Each workflow function is decorated with ``@app.workflow`` from the AOS Client
SDK.  The SDK handles all Azure Functions scaffolding (HTTP triggers,
Service Bus triggers, authentication, health endpoints).

Orchestrations are **perpetual and purpose-driven**: each workflow starts an
ongoing orchestration guided by a purpose.  Agents work toward the purpose
continuously — there is no finite task to complete.

Enterprise capabilities (v4.0.0) demonstrate the new SDK APIs for knowledge
management, risk registry, audit trails, covenants, analytics, MCP
integration, agent interaction, and network discovery.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from aos_client import (
    AOSApp,
    AOSClient,
    AgentDescriptor,
    WorkflowRequest,
    workflow_template,
)
from aos_client.observability import ObservabilityConfig
from typing import Callable

logger = logging.getLogger(__name__)

app = AOSApp(
    name="business-infinity",
    observability=ObservabilityConfig(
        structured_logging=True,
        correlation_tracking=True,
        health_checks=["aos", "service-bus"],
    ),
)

# ── C-Suite Agent Selection ──────────────────────────────────────────────────

#: Agent types considered part of the C-suite
C_SUITE_TYPES = {"LeadershipAgent", "CMOAgent"}

#: Preferred C-suite agent IDs for BusinessInfinity orchestrations
C_SUITE_AGENT_IDS = ["ceo", "cfo", "cmo", "coo", "cto"]


async def select_c_suite_agents(client: AOSClient) -> List[AgentDescriptor]:
    """Select C-suite agents from the RealmOfAgents catalog.

    Returns agents matching :data:`C_SUITE_AGENT_IDS` or, if not found,
    agents whose ``agent_type`` is in :data:`C_SUITE_TYPES`.
    """
    all_agents = await client.list_agents()

    # Prefer explicit IDs
    by_id = {a.agent_id: a for a in all_agents}
    selected = [by_id[aid] for aid in C_SUITE_AGENT_IDS if aid in by_id]

    if not selected:
        # Fall back to type-based selection
        selected = [a for a in all_agents if a.agent_type in C_SUITE_TYPES]

    logger.info("Selected %d C-suite agents: %s", len(selected), [a.agent_id for a in selected])
    return selected


# ── Workflow Template (Enhancement #11) ──────────────────────────────────────


@workflow_template
async def c_suite_orchestration(
    request: WorkflowRequest,
    agent_filter: Callable[[AgentDescriptor], bool],
    purpose: str,
    purpose_scope: str,
) -> Dict[str, Any]:
    """Reusable template for C-suite orchestrations."""
    agents = await select_c_suite_agents(request.client)
    agent_ids = [a.agent_id for a in agents if agent_filter(a)]
    if not agent_ids:
        raise ValueError("No matching agents available in the catalog")
    status = await request.client.start_orchestration(
        agent_ids=agent_ids,
        purpose=purpose,
        purpose_scope=purpose_scope,
        context=request.body,
    )
    return {"orchestration_id": status.orchestration_id, "status": status.status.value}


# ── Purpose-Driven Orchestrations ────────────────────────────────────────────


@app.workflow("strategic-review")
async def strategic_review(request: WorkflowRequest) -> Dict[str, Any]:
    """Start a perpetual strategic review orchestration with C-suite agents.

    The orchestration continuously drives strategic alignment, review, and
    improvement across the organisation.  It does not complete — agents
    work toward the purpose indefinitely.

    Request body::

        {"quarter": "Q1-2026", "focus_areas": ["revenue", "growth"]}
    """
    return await c_suite_orchestration(
        request,
        agent_filter=lambda a: True,
        purpose="Drive strategic review and continuous organisational improvement",
        purpose_scope="C-suite strategic alignment and cross-functional coordination",
    )


@app.workflow("market-analysis")
async def market_analysis(request: WorkflowRequest) -> Dict[str, Any]:
    """Start a perpetual market analysis orchestration led by the CMO agent.

    The orchestration continuously monitors markets, analyses competitors,
    and surfaces insights.  It does not complete — agents work toward the
    purpose indefinitely.

    Request body::

        {"market": "EU SaaS", "competitors": ["AcmeCorp", "Globex"]}
    """
    # Select CMO + supporting agents
    agents = await select_c_suite_agents(request.client)
    agent_ids = [a.agent_id for a in agents if a.agent_type == "CMOAgent"]

    # Add CEO for strategic oversight if available
    ceo = [a for a in agents if a.agent_id == "ceo"]
    if ceo and ceo[0].agent_id not in agent_ids:
        agent_ids.insert(0, ceo[0].agent_id)

    if not agent_ids:
        raise ValueError("No CMO or CEO agents available in the catalog")

    status = await request.client.start_orchestration(
        agent_ids=agent_ids,
        purpose="Continuously analyse markets and surface competitive insights",
        purpose_scope="Market intelligence, competitor monitoring, and opportunity identification",
        context={
            "market": request.body.get("market", ""),
            "competitors": request.body.get("competitors", []),
        },
        workflow="hierarchical",
    )
    logger.info("Market analysis orchestration started: %s", status.orchestration_id)
    return {"orchestration_id": status.orchestration_id, "status": status.status.value}


@app.workflow("budget-approval")
async def budget_approval(request: WorkflowRequest) -> Dict[str, Any]:
    """Start a perpetual budget governance orchestration with C-suite leadership.

    The orchestration continuously oversees budget allocation, monitors
    spend, and governs financial decisions.  It does not complete — agents
    work toward the purpose indefinitely.

    Request body::

        {"department": "Marketing", "amount": 500000, "justification": "Q2 campaign"}
    """
    agents = await select_c_suite_agents(request.client)
    # Budget governance: CEO + CFO
    agent_ids = [a.agent_id for a in agents if a.agent_id in ("ceo", "cfo")]

    if not agent_ids:
        raise ValueError("CEO and/or CFO agents not available in the catalog")

    status = await request.client.start_orchestration(
        agent_ids=agent_ids,
        purpose="Govern budget allocation and ensure fiscal responsibility",
        purpose_scope="Financial governance, budget oversight, and resource allocation",
        context={
            "department": request.body.get("department", ""),
            "amount": request.body.get("amount", 0),
            "justification": request.body.get("justification", ""),
        },
        workflow="sequential",
    )
    logger.info(
        "Budget governance orchestration started: %s",
        status.orchestration_id,
    )
    return {"orchestration_id": status.orchestration_id, "status": status.status.value}


# ── Enterprise Capability Workflows (Enhancement #1–#12) ────────────────────


@app.workflow("knowledge-search")
async def knowledge_search(request: WorkflowRequest) -> Dict[str, Any]:
    """Search the knowledge base.

    Request body::

        {"query": "sustainability policy", "doc_type": "policy", "limit": 5}
    """
    docs = await request.client.search_documents(
        query=request.body.get("query", ""),
        doc_type=request.body.get("doc_type"),
        limit=request.body.get("limit", 10),
    )
    return {"documents": [d.model_dump(mode="json") for d in docs]}


@app.workflow("risk-register")
async def risk_register(request: WorkflowRequest) -> Dict[str, Any]:
    """Register a new risk.

    Request body::

        {"title": "Supply chain disruption", "description": "...",
         "category": "operational", "owner": "coo"}
    """
    risk = await request.client.register_risk(request.body)
    return risk.model_dump(mode="json")


@app.workflow("risk-assess")
async def risk_assess(request: WorkflowRequest) -> Dict[str, Any]:
    """Assess an existing risk.

    Request body::

        {"risk_id": "risk-abc", "likelihood": 0.7, "impact": 0.9}
    """
    risk = await request.client.assess_risk(
        risk_id=request.body["risk_id"],
        likelihood=request.body["likelihood"],
        impact=request.body["impact"],
    )
    return risk.model_dump(mode="json")


@app.workflow("log-decision")
async def log_decision_workflow(request: WorkflowRequest) -> Dict[str, Any]:
    """Log a boardroom decision.

    Request body::

        {"title": "Expand to EU", "rationale": "Market opportunity",
         "agent_id": "ceo"}
    """
    record = await request.client.log_decision(request.body)
    return record.model_dump(mode="json")


@app.workflow("covenant-create")
async def covenant_create(request: WorkflowRequest) -> Dict[str, Any]:
    """Create a business covenant.

    Request body::

        {"title": "Ethics Covenant", "parties": ["business-infinity"]}
    """
    covenant = await request.client.create_covenant(request.body)
    return covenant.model_dump(mode="json")


@app.workflow("ask-agent")
async def ask_agent_workflow(request: WorkflowRequest) -> Dict[str, Any]:
    """Ask a single agent a question.

    Request body::

        {"agent_id": "ceo", "message": "What is the Q2 strategy?"}
    """
    response = await request.client.ask_agent(
        agent_id=request.body["agent_id"],
        message=request.body["message"],
        context=request.body.get("context"),
    )
    return response.model_dump(mode="json")


# ── Orchestration Update Handler (Enhancement #5) ───────────────────────────


@app.on_orchestration_update("strategic-review")
async def handle_strategic_review_update(update) -> None:
    """Handle intermediate updates from strategic review orchestrations."""
    logger.info(
        "Strategic review update from agent %s: %s",
        getattr(update, "agent_id", "unknown"),
        getattr(update, "output", ""),
    )


# ── MCP Tool Integration (Enhancement #7) ───────────────────────────────────


@app.mcp_tool("erp-search")
async def erp_search(request) -> Any:
    """Search ERP via MCP server."""
    return await request.client.call_mcp_tool("erpnext", "search", request.body)


# ── Further Enhancement Workflows (v5.0.0) ──────────────────────────────────


@app.workflow("risk-heatmap")
async def risk_heatmap(request: WorkflowRequest) -> Dict[str, Any]:
    """Get risk heatmap for the boardroom.

    Request body::

        {"category": "operational"}  # optional category filter
    """
    heatmap = await request.client.get_risk_heatmap(
        category=request.body.get("category"),
    )
    return heatmap.model_dump(mode="json")


@app.workflow("risk-summary")
async def risk_summary(request: WorkflowRequest) -> Dict[str, Any]:
    """Get aggregate risk summary.

    Request body::

        {"category": "financial"}  # optional category filter
    """
    summary = await request.client.get_risk_summary(
        category=request.body.get("category"),
    )
    return summary.model_dump(mode="json")


@app.workflow("compliance-report")
async def compliance_report(request: WorkflowRequest) -> Dict[str, Any]:
    """Generate a compliance report for regulatory submissions.

    Request body::

        {"start_time": "2026-01-01T00:00:00", "end_time": "2026-03-31T23:59:59",
         "report_type": "decisions"}
    """
    from datetime import datetime

    report = await request.client.generate_compliance_report(
        start_time=datetime.fromisoformat(request.body["start_time"]),
        end_time=datetime.fromisoformat(request.body["end_time"]),
        report_type=request.body.get("report_type", "decisions"),
    )
    return report.model_dump(mode="json")


@app.workflow("create-alert")
async def create_alert_workflow(request: WorkflowRequest) -> Dict[str, Any]:
    """Create a metric alert.

    Request body::

        {"metric_name": "risk_score", "threshold": 8.0, "condition": "gt"}
    """
    alert = await request.client.create_alert(
        metric_name=request.body["metric_name"],
        threshold=request.body["threshold"],
        condition=request.body.get("condition", "gt"),
    )
    return alert.model_dump(mode="json")


@app.workflow("register-webhook")
async def register_webhook_workflow(request: WorkflowRequest) -> Dict[str, Any]:
    """Register a webhook for external notifications.

    Request body::

        {"url": "https://hooks.slack.com/...", "events": ["decision.created"]}
    """
    webhook = await request.client.register_webhook(
        url=request.body["url"],
        events=request.body["events"],
    )
    return webhook.model_dump(mode="json")


# ── Covenant Event Handlers (v5.0.0 Enhancement #3) ─────────────────────────


@app.on_covenant_event("violated")
async def handle_covenant_violation(event) -> None:
    """Handle covenant violation events."""
    logger.warning(
        "Covenant %s violated: %s",
        getattr(event, "covenant_id", "unknown"),
        getattr(event, "details", {}),
    )


@app.on_covenant_event("expiring")
async def handle_covenant_expiring(event) -> None:
    """Handle covenant expiration warnings."""
    logger.info(
        "Covenant %s nearing expiration: %s",
        getattr(event, "covenant_id", "unknown"),
        getattr(event, "details", {}),
    )


# ── MCP Event Handlers (v5.0.0 Enhancement #8) ──────────────────────────────


@app.on_mcp_event("erpnext", "order_created")
async def handle_erp_order(event) -> None:
    """Handle ERP order creation events."""
    logger.info(
        "ERP order created: %s",
        getattr(event, "payload", {}),
    )


# ── Webhook Handler (v5.0.0 Enhancement #12) ────────────────────────────────


@app.webhook("slack-notifications")
async def notify_slack(event) -> None:
    """Send notification to Slack when significant events occur."""
    logger.info(
        "Slack notification: %s",
        getattr(event, "payload", {}),
    )
