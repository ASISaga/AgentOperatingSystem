"""Main Azure Functions entry point for AOS.

Exposes AOS orchestration capabilities as HTTP endpoints.  Client applications
submit orchestration requests (selecting agents from the RealmOfAgents catalog)
and retrieve results through these endpoints.

Endpoints:
    POST /api/orchestrations           Submit an orchestration request
    GET  /api/orchestrations/{id}      Poll orchestration status
    GET  /api/orchestrations/{id}/result  Retrieve completed result
    POST /api/orchestrations/{id}/cancel  Cancel a running orchestration
    GET  /api/health                   Health check
"""

from __future__ import annotations

import json
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict

import azure.functions as func

logger = logging.getLogger(__name__)
app = func.FunctionApp()

# ── In-Memory Orchestration Store ─────────────────────────────────────────────
# Development/prototype only.  Data is lost on restart and not shared across
# instances.  In production, replace with Azure Table Storage or Cosmos DB.

_orchestrations: Dict[str, Dict[str, Any]] = {}


# ── HTTP Endpoints ───────────────────────────────────────────────────────────


@app.function_name("submit_orchestration")
@app.route(route="orchestrations", methods=["POST"])
async def submit_orchestration(req: func.HttpRequest) -> func.HttpResponse:
    """Submit an orchestration request.

    Request body (OrchestrationRequest)::

        {
            "orchestration_id": "optional-client-id",
            "agent_ids": ["ceo", "cfo", "cmo"],
            "workflow": "collaborative",
            "task": {"type": "strategic_review", "data": {...}},
            "config": {},
            "callback_url": null
        }
    """
    try:
        body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON body"}),
            status_code=400,
            mimetype="application/json",
        )

    agent_ids = body.get("agent_ids", [])
    if not agent_ids:
        return func.HttpResponse(
            json.dumps({"error": "agent_ids must be a non-empty list"}),
            status_code=400,
            mimetype="application/json",
        )

    orch_id = body.get("orchestration_id") or str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    record: Dict[str, Any] = {
        "orchestration_id": orch_id,
        "status": "pending",
        "agent_ids": agent_ids,
        "workflow": body.get("workflow", "collaborative"),
        "task": body.get("task", {}),
        "config": body.get("config", {}),
        "callback_url": body.get("callback_url"),
        "progress": 0.0,
        "created_at": now,
        "updated_at": now,
        "error": None,
        "results": {},
        "summary": None,
    }
    _orchestrations[orch_id] = record

    logger.info(
        "Orchestration %s submitted — agents=%s workflow=%s",
        orch_id,
        agent_ids,
        record["workflow"],
    )

    # TODO: Dispatch to aos-kernel orchestration engine via Service Bus or direct call

    status_response = {
        "orchestration_id": orch_id,
        "status": "pending",
        "agent_ids": agent_ids,
        "progress": 0.0,
        "created_at": now,
        "updated_at": now,
        "error": None,
    }
    return func.HttpResponse(
        json.dumps(status_response),
        status_code=202,
        mimetype="application/json",
    )


@app.function_name("get_orchestration_status")
@app.route(route="orchestrations/{orchestration_id}", methods=["GET"])
async def get_orchestration_status(req: func.HttpRequest) -> func.HttpResponse:
    """Poll the status of a submitted orchestration."""
    orch_id = req.route_params.get("orchestration_id", "")
    record = _orchestrations.get(orch_id)

    if record is None:
        return func.HttpResponse(
            json.dumps({"error": f"Orchestration '{orch_id}' not found"}),
            status_code=404,
            mimetype="application/json",
        )

    return func.HttpResponse(
        json.dumps({
            "orchestration_id": record["orchestration_id"],
            "status": record["status"],
            "agent_ids": record["agent_ids"],
            "progress": record["progress"],
            "created_at": record["created_at"],
            "updated_at": record["updated_at"],
            "error": record["error"],
        }),
        mimetype="application/json",
    )


@app.function_name("get_orchestration_result")
@app.route(route="orchestrations/{orchestration_id}/result", methods=["GET"])
async def get_orchestration_result(req: func.HttpRequest) -> func.HttpResponse:
    """Retrieve the final result of a completed orchestration."""
    orch_id = req.route_params.get("orchestration_id", "")
    record = _orchestrations.get(orch_id)

    if record is None:
        return func.HttpResponse(
            json.dumps({"error": f"Orchestration '{orch_id}' not found"}),
            status_code=404,
            mimetype="application/json",
        )

    if record["status"] not in ("completed", "failed"):
        return func.HttpResponse(
            json.dumps({"error": "Orchestration has not completed yet", "status": record["status"]}),
            status_code=409,
            mimetype="application/json",
        )

    return func.HttpResponse(
        json.dumps({
            "orchestration_id": record["orchestration_id"],
            "status": record["status"],
            "agent_ids": record["agent_ids"],
            "results": record["results"],
            "summary": record["summary"],
            "created_at": record["created_at"],
            "completed_at": record.get("completed_at"),
            "duration_seconds": record.get("duration_seconds"),
        }),
        mimetype="application/json",
    )


@app.function_name("cancel_orchestration")
@app.route(route="orchestrations/{orchestration_id}/cancel", methods=["POST"])
async def cancel_orchestration(req: func.HttpRequest) -> func.HttpResponse:
    """Cancel a running orchestration."""
    orch_id = req.route_params.get("orchestration_id", "")
    record = _orchestrations.get(orch_id)

    if record is None:
        return func.HttpResponse(
            json.dumps({"error": f"Orchestration '{orch_id}' not found"}),
            status_code=404,
            mimetype="application/json",
        )

    if record["status"] in ("completed", "failed", "cancelled"):
        return func.HttpResponse(
            json.dumps({"error": f"Cannot cancel orchestration in '{record['status']}' state"}),
            status_code=409,
            mimetype="application/json",
        )

    record["status"] = "cancelled"
    record["updated_at"] = datetime.now(timezone.utc).isoformat()
    logger.info("Orchestration %s cancelled", orch_id)

    return func.HttpResponse(
        json.dumps({
            "orchestration_id": record["orchestration_id"],
            "status": "cancelled",
            "agent_ids": record["agent_ids"],
            "progress": record["progress"],
            "created_at": record["created_at"],
            "updated_at": record["updated_at"],
            "error": None,
        }),
        mimetype="application/json",
    )


@app.function_name("health")
@app.route(route="health", methods=["GET"])
async def health(req: func.HttpRequest) -> func.HttpResponse:
    """Health check endpoint."""
    return func.HttpResponse(
        json.dumps({
            "app": "aos-function-app",
            "status": "healthy",
            "active_orchestrations": len(
                [o for o in _orchestrations.values() if o["status"] in ("pending", "running")]
            ),
        }),
        mimetype="application/json",
    )
