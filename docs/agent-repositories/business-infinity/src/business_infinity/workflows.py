"""BusinessInfinity workflows — pure business logic orchestrations.

Each workflow function defines WHAT to do (business logic), not HOW to do it
(infrastructure).  The ``aos_client`` SDK handles communication with AOS.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from aos_client import AOSClient, AgentDescriptor

logger = logging.getLogger(__name__)

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

async def run_strategic_review(
    client: AOSClient,
    quarter: str,
    focus_areas: List[str] | None = None,
) -> Dict[str, Any]:
    """Run a quarterly strategic review with C-suite agents.

    This is a pure business-logic workflow.  AOS handles agent lifecycle,
    orchestration, messaging, and result aggregation.

    Args:
        client: Authenticated :class:`AOSClient`.
        quarter: Quarter identifier (e.g. ``"Q1-2026"``).
        focus_areas: Optional list of focus areas for the review.

    Returns:
        Orchestration result dictionary.
    """
    agents = await select_c_suite_agents(client)
    agent_ids = [a.agent_id for a in agents]

    result = await client.run_orchestration(
        agent_ids=agent_ids,
        task={
            "type": "strategic_review",
            "data": {
                "quarter": quarter,
                "focus_areas": focus_areas or ["revenue", "growth", "efficiency"],
            },
        },
        workflow="collaborative",
    )
    logger.info("Strategic review for %s complete: %s", quarter, result.summary)
    return result.model_dump()


async def run_market_analysis(
    client: AOSClient,
    market: str,
    competitors: List[str] | None = None,
) -> Dict[str, Any]:
    """Run a market analysis led by the CMO agent.

    Args:
        client: Authenticated :class:`AOSClient`.
        market: Target market name.
        competitors: Optional list of competitor names.

    Returns:
        Orchestration result dictionary.
    """
    # Select CMO + supporting agents
    agents = await select_c_suite_agents(client)
    agent_ids = [a.agent_id for a in agents if a.agent_type == "CMOAgent"]

    # Add CEO for strategic oversight if available
    ceo = [a for a in agents if a.agent_id == "ceo"]
    if ceo and ceo[0].agent_id not in agent_ids:
        agent_ids.insert(0, ceo[0].agent_id)

    if not agent_ids:
        raise ValueError("No CMO or CEO agents available in the catalog")

    result = await client.run_orchestration(
        agent_ids=agent_ids,
        task={
            "type": "market_analysis",
            "data": {
                "market": market,
                "competitors": competitors or [],
            },
        },
        workflow="hierarchical",
    )
    logger.info("Market analysis for %s complete: %s", market, result.summary)
    return result.model_dump()


async def run_budget_approval(
    client: AOSClient,
    department: str,
    amount: float,
    justification: str,
) -> Dict[str, Any]:
    """Submit a budget approval request to C-suite leadership.

    Args:
        client: Authenticated :class:`AOSClient`.
        department: Department requesting the budget.
        amount: Requested budget amount.
        justification: Business justification.

    Returns:
        Orchestration result dictionary containing the approval decision.
    """
    agents = await select_c_suite_agents(client)
    # Budget approvals: CEO + CFO
    agent_ids = [a.agent_id for a in agents if a.agent_id in ("ceo", "cfo")]

    if not agent_ids:
        raise ValueError("CEO and/or CFO agents not available in the catalog")

    result = await client.run_orchestration(
        agent_ids=agent_ids,
        task={
            "type": "budget_approval",
            "data": {
                "department": department,
                "amount": amount,
                "justification": justification,
            },
        },
        workflow="sequential",
    )
    logger.info("Budget approval for %s ($%.0f): %s", department, amount, result.summary)
    return result.model_dump()
