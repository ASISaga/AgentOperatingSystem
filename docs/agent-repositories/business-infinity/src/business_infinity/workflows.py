"""BusinessInfinity workflows — pure business logic orchestrations.

Each workflow function is decorated with ``@app.workflow`` from the AOS Client
SDK.  The SDK handles all Azure Functions scaffolding (HTTP triggers,
Service Bus triggers, authentication, health endpoints).

Client applications define WHAT to do (business logic), not HOW to do it.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from aos_client import AOSApp, AOSClient, AgentDescriptor, WorkflowRequest

logger = logging.getLogger(__name__)

app = AOSApp(name="business-infinity")

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


# ── Business Workflows ───────────────────────────────────────────────────────


@app.workflow("strategic-review")
async def strategic_review(request: WorkflowRequest) -> Dict[str, Any]:
    """Run a quarterly strategic review with C-suite agents.

    Request body::

        {"quarter": "Q1-2026", "focus_areas": ["revenue", "growth"]}
    """
    quarter = request.body.get("quarter")
    if not quarter:
        raise ValueError("quarter is required")

    agents = await select_c_suite_agents(request.client)
    agent_ids = [a.agent_id for a in agents]

    result = await request.client.run_orchestration(
        agent_ids=agent_ids,
        task={
            "type": "strategic_review",
            "data": {
                "quarter": quarter,
                "focus_areas": request.body.get("focus_areas", ["revenue", "growth", "efficiency"]),
            },
        },
        workflow="collaborative",
    )
    logger.info("Strategic review for %s complete: %s", quarter, result.summary)
    return result.model_dump()


@app.workflow("market-analysis")
async def market_analysis(request: WorkflowRequest) -> Dict[str, Any]:
    """Run a market analysis led by the CMO agent.

    Request body::

        {"market": "EU SaaS", "competitors": ["AcmeCorp", "Globex"]}
    """
    market = request.body.get("market")
    if not market:
        raise ValueError("market is required")

    # Select CMO + supporting agents
    agents = await select_c_suite_agents(request.client)
    agent_ids = [a.agent_id for a in agents if a.agent_type == "CMOAgent"]

    # Add CEO for strategic oversight if available
    ceo = [a for a in agents if a.agent_id == "ceo"]
    if ceo and ceo[0].agent_id not in agent_ids:
        agent_ids.insert(0, ceo[0].agent_id)

    if not agent_ids:
        raise ValueError("No CMO or CEO agents available in the catalog")

    result = await request.client.run_orchestration(
        agent_ids=agent_ids,
        task={
            "type": "market_analysis",
            "data": {
                "market": market,
                "competitors": request.body.get("competitors", []),
            },
        },
        workflow="hierarchical",
    )
    logger.info("Market analysis for %s complete: %s", market, result.summary)
    return result.model_dump()


@app.workflow("budget-approval")
async def budget_approval(request: WorkflowRequest) -> Dict[str, Any]:
    """Submit a budget approval request to C-suite leadership.

    Request body::

        {"department": "Marketing", "amount": 500000, "justification": "Q2 campaign"}
    """
    required = ("department", "amount", "justification")
    missing = [f for f in required if f not in request.body]
    if missing:
        raise ValueError(f"Missing required fields: {missing}")

    agents = await select_c_suite_agents(request.client)
    # Budget approvals: CEO + CFO
    agent_ids = [a.agent_id for a in agents if a.agent_id in ("ceo", "cfo")]

    if not agent_ids:
        raise ValueError("CEO and/or CFO agents not available in the catalog")

    result = await request.client.run_orchestration(
        agent_ids=agent_ids,
        task={
            "type": "budget_approval",
            "data": {
                "department": request.body["department"],
                "amount": float(request.body["amount"]),
                "justification": request.body["justification"],
            },
        },
        workflow="sequential",
    )
    logger.info(
        "Budget approval for %s ($%.0f): %s",
        request.body["department"],
        float(request.body["amount"]),
        result.summary,
    )
    return result.model_dump()
