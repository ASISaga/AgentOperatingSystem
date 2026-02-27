"""Main Azure Functions entry point for AOS.

Exposes AOS orchestration capabilities as HTTP endpoints and Azure Service Bus
triggers.  Client applications submit orchestration requests (selecting agents
from the RealmOfAgents catalog) and retrieve results through these endpoints.

Endpoints:
    POST /api/orchestrations              Submit an orchestration request (HTTP)
    GET  /api/orchestrations/{id}         Poll orchestration status
    GET  /api/orchestrations/{id}/result  Retrieve completed result
    POST /api/orchestrations/{id}/cancel  Cancel a running orchestration
    POST /api/apps/register               Register a client application
    GET  /api/apps/{app_name}             Get app registration status
    DELETE /api/apps/{app_name}           Deregister a client application
    GET  /api/health                      Health check

Service Bus Triggers:
    aos-orchestration-requests            Process incoming orchestration requests
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

# ── In-Memory Stores ──────────────────────────────────────────────────────────
# Development/prototype only.  In production, replace with Azure Table Storage
# or Cosmos DB.

_orchestrations: Dict[str, Dict[str, Any]] = {}
_registered_apps: Dict[str, Dict[str, Any]] = {}


# ── HTTP Endpoints — Orchestrations ──────────────────────────────────────────


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

    return _process_orchestration_request(body)


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


# ── Service Bus Trigger — Orchestration Requests ────────────────────────────


@app.function_name("service_bus_orchestration_request")
@app.service_bus_queue_trigger(
    arg_name="msg",
    queue_name="aos-orchestration-requests",
    connection="SERVICE_BUS_CONNECTION",
)
async def service_bus_orchestration_request(msg: func.ServiceBusMessage) -> None:
    """Process an orchestration request received via Service Bus.

    This trigger enables scale-to-zero: AOS sleeps until a message arrives
    on the orchestration requests queue, then wakes up to process it.
    """
    body_bytes = msg.get_body()
    body_str = body_bytes.decode("utf-8")

    try:
        envelope = json.loads(body_str)
    except json.JSONDecodeError:
        logger.error("Invalid JSON in Service Bus message: %s", body_str[:200])
        return

    app_name = envelope.get("app_name", "unknown")
    payload = envelope.get("payload", {})

    logger.info(
        "Received orchestration request via Service Bus from app '%s'",
        app_name,
    )

    # Process the request using the same logic as HTTP
    _process_orchestration_request(payload, source_app=app_name)

    # TODO: Send result back via Service Bus topic to the client app
    # This would use the aos-orchestration-results topic with a subscription
    # filtered by app_name.


# ── HTTP Endpoints — App Registration ────────────────────────────────────────


@app.function_name("register_app")
@app.route(route="apps/register", methods=["POST"])
async def register_app(req: func.HttpRequest) -> func.HttpResponse:
    """Register a client application with AOS.

    Provisions Service Bus queues, topics, and subscriptions for async
    communication.  Returns connection details to the client.

    Request body::

        {
            "app_name": "business-infinity",
            "workflows": ["strategic-review", "market-analysis"],
            "app_id": "optional-azure-ad-app-id"
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

    app_name = body.get("app_name")
    if not app_name:
        return func.HttpResponse(
            json.dumps({"error": "app_name is required"}),
            status_code=400,
            mimetype="application/json",
        )

    # Create registration record
    subscription_name = app_name
    registration = {
        "app_name": app_name,
        "app_id": body.get("app_id"),
        "workflows": body.get("workflows", []),
        "request_queue": "aos-orchestration-requests",
        "result_topic": "aos-orchestration-results",
        "result_subscription": subscription_name,
        "status": "provisioned",
        "provisioned_resources": {
            "service_bus_queue": "aos-orchestration-requests",
            "service_bus_topic": "aos-orchestration-results",
            "service_bus_subscription": subscription_name,
        },
        "service_bus_connection_string": os.environ.get("SERVICE_BUS_CONNECTION"),
    }

    _registered_apps[app_name] = registration

    logger.info(
        "Registered app '%s' — workflows=%s subscription=%s",
        app_name,
        registration["workflows"],
        subscription_name,
    )

    # TODO: Actually provision Service Bus resources via Azure SDK
    # - Create subscription on aos-orchestration-results topic filtered by app_name
    # - Set up managed identity role assignments

    return func.HttpResponse(
        json.dumps(registration),
        status_code=201,
        mimetype="application/json",
    )


@app.function_name("get_app_registration")
@app.route(route="apps/{app_name}", methods=["GET"])
async def get_app_registration(req: func.HttpRequest) -> func.HttpResponse:
    """Get the registration status of a client application."""
    app_name = req.route_params.get("app_name", "")
    registration = _registered_apps.get(app_name)

    if registration is None:
        return func.HttpResponse(
            json.dumps({"error": f"App '{app_name}' not registered"}),
            status_code=404,
            mimetype="application/json",
        )

    return func.HttpResponse(
        json.dumps(registration),
        mimetype="application/json",
    )


@app.function_name("deregister_app")
@app.route(route="apps/{app_name}", methods=["DELETE"])
async def deregister_app(req: func.HttpRequest) -> func.HttpResponse:
    """Remove a client application registration."""
    app_name = req.route_params.get("app_name", "")

    if app_name not in _registered_apps:
        return func.HttpResponse(
            json.dumps({"error": f"App '{app_name}' not registered"}),
            status_code=404,
            mimetype="application/json",
        )

    del _registered_apps[app_name]
    logger.info("Deregistered app '%s'", app_name)

    # TODO: Clean up provisioned Service Bus resources

    return func.HttpResponse(status_code=204)


# ── Health ───────────────────────────────────────────────────────────────────


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
            "registered_apps": list(_registered_apps.keys()),
        }),
        mimetype="application/json",
    )


# ── Internal Helpers ─────────────────────────────────────────────────────────


def _process_orchestration_request(
    body: Dict[str, Any],
    source_app: str | None = None,
) -> func.HttpResponse:
    """Process an orchestration request from HTTP or Service Bus.

    Args:
        body: Parsed request body.
        source_app: Name of the source client app (for Service Bus requests).

    Returns:
        HTTP response with orchestration status.
    """
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
        "source_app": source_app,
        "progress": 0.0,
        "created_at": now,
        "updated_at": now,
        "error": None,
        "results": {},
        "summary": None,
    }
    _orchestrations[orch_id] = record

    logger.info(
        "Orchestration %s submitted — agents=%s workflow=%s source=%s",
        orch_id,
        agent_ids,
        record["workflow"],
        source_app or "http",
    )

    # TODO: Dispatch to aos-kernel orchestration engine

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
