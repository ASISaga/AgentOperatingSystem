"""BusinessInfinity Azure Functions entry point.

A lean function app that contains only HTTP triggers for business workflows.
All agent orchestration is delegated to AOS via the ``aos_client`` SDK.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict

import azure.functions as func

from aos_client import AOSClient
from business_infinity.workflows import (
    run_budget_approval,
    run_market_analysis,
    run_strategic_review,
)

logger = logging.getLogger(__name__)
app = func.FunctionApp()

# ── Configuration ────────────────────────────────────────────────────────────

AOS_ENDPOINT = os.environ.get("AOS_ENDPOINT", "http://localhost:7071")
REALM_ENDPOINT = os.environ.get("REALM_ENDPOINT", AOS_ENDPOINT)


def _get_client() -> AOSClient:
    """Create an AOSClient.  In production, add Azure credential."""
    return AOSClient(endpoint=AOS_ENDPOINT, realm_endpoint=REALM_ENDPOINT)


# ── HTTP Triggers ────────────────────────────────────────────────────────────


@app.function_name("strategic_review")
@app.route(route="workflows/strategic-review", methods=["POST"])
async def strategic_review(req: func.HttpRequest) -> func.HttpResponse:
    """Run a quarterly strategic review with C-suite agents.

    Request body::

        {"quarter": "Q1-2026", "focus_areas": ["revenue", "growth"]}
    """
    body = req.get_json()
    quarter = body.get("quarter")
    if not quarter:
        return func.HttpResponse(
            json.dumps({"error": "quarter is required"}),
            status_code=400,
            mimetype="application/json",
        )

    async with _get_client() as client:
        result = await run_strategic_review(
            client,
            quarter=quarter,
            focus_areas=body.get("focus_areas"),
        )

    return func.HttpResponse(
        json.dumps(result, default=str),
        mimetype="application/json",
    )


@app.function_name("market_analysis")
@app.route(route="workflows/market-analysis", methods=["POST"])
async def market_analysis(req: func.HttpRequest) -> func.HttpResponse:
    """Run a market analysis led by the CMO agent.

    Request body::

        {"market": "EU SaaS", "competitors": ["AcmeCorp", "Globex"]}
    """
    body = req.get_json()
    market = body.get("market")
    if not market:
        return func.HttpResponse(
            json.dumps({"error": "market is required"}),
            status_code=400,
            mimetype="application/json",
        )

    async with _get_client() as client:
        result = await run_market_analysis(
            client,
            market=market,
            competitors=body.get("competitors"),
        )

    return func.HttpResponse(
        json.dumps(result, default=str),
        mimetype="application/json",
    )


@app.function_name("budget_approval")
@app.route(route="workflows/budget-approval", methods=["POST"])
async def budget_approval(req: func.HttpRequest) -> func.HttpResponse:
    """Submit a budget approval request to C-suite leadership.

    Request body::

        {"department": "Marketing", "amount": 500000, "justification": "Q2 campaign"}
    """
    body = req.get_json()
    required = ("department", "amount", "justification")
    missing = [f for f in required if f not in body]
    if missing:
        return func.HttpResponse(
            json.dumps({"error": f"Missing required fields: {missing}"}),
            status_code=400,
            mimetype="application/json",
        )

    async with _get_client() as client:
        result = await run_budget_approval(
            client,
            department=body["department"],
            amount=float(body["amount"]),
            justification=body["justification"],
        )

    return func.HttpResponse(
        json.dumps(result, default=str),
        mimetype="application/json",
    )


@app.function_name("health")
@app.route(route="health", methods=["GET"])
async def health(req: func.HttpRequest) -> func.HttpResponse:
    """Health check — verifies connectivity to AOS."""
    try:
        async with _get_client() as client:
            aos_health = await client.health_check()
        status: Dict[str, Any] = {
            "app": "business-infinity",
            "status": "healthy",
            "aos": aos_health,
        }
        return func.HttpResponse(json.dumps(status), mimetype="application/json")
    except Exception as exc:
        return func.HttpResponse(
            json.dumps({"app": "business-infinity", "status": "degraded", "error": str(exc)}),
            status_code=503,
            mimetype="application/json",
        )
