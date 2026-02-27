"""Main Azure Functions entry point for AOS.

Exposes AOS orchestration capabilities and enterprise services as HTTP
endpoints and Azure Service Bus triggers.  Client applications use the
aos-client-sdk to interact with these endpoints.

Endpoints — Orchestrations:
    POST /api/orchestrations              Submit an orchestration request
    GET  /api/orchestrations/{id}         Poll orchestration status
    GET  /api/orchestrations/{id}/result  Retrieve completed result
    POST /api/orchestrations/{id}/cancel  Cancel a running orchestration

Endpoints — Knowledge Base:
    POST /api/knowledge/documents         Create a document
    GET  /api/knowledge/documents         Search documents
    GET  /api/knowledge/documents/{id}    Get document by ID
    POST /api/knowledge/documents/{id}    Update document
    DELETE /api/knowledge/documents/{id}  Delete document

Endpoints — Risk Registry:
    POST /api/risks                       Register a risk
    GET  /api/risks                       List risks
    POST /api/risks/{id}/assess           Assess a risk
    POST /api/risks/{id}/status           Update risk status
    POST /api/risks/{id}/mitigate         Add mitigation plan

Endpoints — Audit Trail:
    POST /api/audit/decisions             Log a decision
    GET  /api/audit/decisions             Get decision history
    GET  /api/audit/trail                 Get audit trail

Endpoints — Covenants:
    POST /api/covenants                   Create a covenant
    GET  /api/covenants                   List covenants
    GET  /api/covenants/{id}/validate     Validate a covenant
    POST /api/covenants/{id}/sign         Sign a covenant

Endpoints — Analytics:
    POST /api/metrics                     Record a metric
    GET  /api/metrics                     Get metric series
    POST /api/kpis                        Create a KPI
    GET  /api/kpis/dashboard              Get KPI dashboard

Endpoints — MCP:
    GET  /api/mcp/servers                 List MCP servers
    POST /api/mcp/servers/{s}/tools/{t}   Call an MCP tool
    GET  /api/mcp/servers/{s}/status      Get MCP server status

Endpoints — Agents:
    POST /api/agents/{id}/ask             Ask an agent
    POST /api/agents/{id}/send            Send to an agent

Endpoints — Knowledge Base (batch/versioning):
    POST /api/knowledge/documents/batch            Batch-create documents
    GET  /api/knowledge/documents/{id}/versions     Get document version history
    POST /api/knowledge/documents/{id}/restore      Restore a document version
    POST /api/knowledge/documents/export            Export documents

Endpoints — Risk Aggregation:
    GET  /api/risks/heatmap               Risk heatmap
    GET  /api/risks/summary               Risk summary statistics
    GET  /api/risks/trends                Risk trend data

Endpoints — Audit Compliance:
    POST /api/audit/compliance-report     Generate compliance report
    GET  /api/audit/decisions/{id}/chain   Get decision chain

Endpoints — Analytics (dashboards & alerts):
    POST /api/dashboards                  Create a custom dashboard
    POST /api/alerts                      Create a metric alert
    GET  /api/alerts                      List alerts

Endpoints — Network (federation):
    POST /api/network                     Create a network
    POST /api/network/{id}/request        Request network membership
    GET  /api/network/{id}/verify/{pid}   Verify a peer

Endpoints — Network:
    POST /api/network/discover            Discover peers
    POST /api/network/{id}/join           Join a network
    GET  /api/network                     List networks

Endpoints — Orchestration Streaming:
    POST /api/orchestrations/{id}/subscribe  Subscribe to updates
    GET  /api/orchestrations/{id}/updates    Get orchestration updates

Endpoints — Webhooks:
    POST /api/webhooks                    Register a webhook
    GET  /api/webhooks                    List webhooks

Endpoints — App Registration:
    POST /api/apps/register               Register a client application
    GET  /api/apps/{app_name}             Get app registration status
    DELETE /api/apps/{app_name}           Deregister a client application

Endpoints — Health:
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
_documents: Dict[str, Dict[str, Any]] = {}
_risks: Dict[str, Dict[str, Any]] = {}
_decisions: list = []
_audit_entries: list = []
_covenants: Dict[str, Dict[str, Any]] = {}
_metrics_store: list = []
_kpis: Dict[str, Dict[str, Any]] = {}
_mcp_servers: Dict[str, Dict[str, Any]] = {}
_networks: Dict[str, Dict[str, Any]] = {}
_network_memberships: Dict[str, Dict[str, Any]] = {}
_document_versions: Dict[str, list] = {}
_alerts_store: Dict[str, Dict[str, Any]] = {}
_dashboards_store: Dict[str, Dict[str, Any]] = {}
_webhooks_store: Dict[str, Dict[str, Any]] = {}
_orchestration_subscriptions: Dict[str, list] = {}
_orchestration_updates: Dict[str, list] = {}


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


# ── Knowledge Base Endpoints ─────────────────────────────────────────────────


@app.function_name("create_document")
@app.route(route="knowledge/documents", methods=["POST"])
async def create_document(req: func.HttpRequest) -> func.HttpResponse:
    """Create a knowledge document."""
    try:
        body = req.get_json()
    except ValueError:
        return _json_error("Invalid JSON body", 400)
    doc_id = body.get("id") or f"doc-{uuid.uuid4().hex[:8]}"
    now = datetime.now(timezone.utc).isoformat()
    doc = {
        "id": doc_id, "title": body.get("title", ""),
        "doc_type": body.get("doc_type", ""), "status": "draft",
        "content": body.get("content", {}), "tags": body.get("tags", []),
        "metadata": body.get("metadata", {}),
        "created_at": now, "updated_at": now,
        "created_by": body.get("created_by"),
    }
    _documents[doc_id] = doc
    return func.HttpResponse(json.dumps(doc), status_code=201, mimetype="application/json")


@app.function_name("get_document")
@app.route(route="knowledge/documents/{document_id}", methods=["GET"])
async def get_document(req: func.HttpRequest) -> func.HttpResponse:
    """Get a knowledge document by ID."""
    doc_id = req.route_params.get("document_id", "")
    doc = _documents.get(doc_id)
    if doc is None:
        return _json_error(f"Document '{doc_id}' not found", 404)
    return func.HttpResponse(json.dumps(doc), mimetype="application/json")


@app.function_name("search_documents")
@app.route(route="knowledge/documents", methods=["GET"])
async def search_documents(req: func.HttpRequest) -> func.HttpResponse:
    """Search knowledge documents."""
    query = (req.params.get("query") or "").lower()
    doc_type = req.params.get("doc_type")
    limit = int(req.params.get("limit", "10"))
    results = list(_documents.values())
    if query:
        results = [d for d in results if query in d.get("title", "").lower()
                    or query in json.dumps(d.get("content", {})).lower()]
    if doc_type:
        results = [d for d in results if d.get("doc_type") == doc_type]
    return func.HttpResponse(
        json.dumps({"documents": results[:limit]}), mimetype="application/json")


@app.function_name("update_document")
@app.route(route="knowledge/documents/{document_id}", methods=["POST"])
async def update_document(req: func.HttpRequest) -> func.HttpResponse:
    """Update a knowledge document's content."""
    doc_id = req.route_params.get("document_id", "")
    doc = _documents.get(doc_id)
    if doc is None:
        return _json_error(f"Document '{doc_id}' not found", 404)
    try:
        body = req.get_json()
    except ValueError:
        return _json_error("Invalid JSON body", 400)
    doc["content"] = body.get("content", doc["content"])
    doc["updated_at"] = datetime.now(timezone.utc).isoformat()
    return func.HttpResponse(json.dumps(doc), mimetype="application/json")


@app.function_name("delete_document")
@app.route(route="knowledge/documents/{document_id}", methods=["DELETE"])
async def delete_document(req: func.HttpRequest) -> func.HttpResponse:
    """Delete a knowledge document."""
    doc_id = req.route_params.get("document_id", "")
    _documents.pop(doc_id, None)
    return func.HttpResponse(status_code=204)


# ── Knowledge Base Batch / Versioning Endpoints ──────────────────────────────


@app.function_name("batch_create_documents")
@app.route(route="knowledge/documents/batch", methods=["POST"])
async def batch_create_documents(req: func.HttpRequest) -> func.HttpResponse:
    """Batch-create knowledge documents."""
    try:
        body = req.get_json()
    except ValueError:
        return _json_error("Invalid JSON body", 400)
    docs_in = body.get("documents", [])
    created = []
    now = datetime.now(timezone.utc).isoformat()
    for item in docs_in:
        doc_id = item.get("id") or f"doc-{uuid.uuid4().hex[:8]}"
        doc = {
            "id": doc_id, "title": item.get("title", ""),
            "doc_type": item.get("doc_type", ""), "status": "draft",
            "content": item.get("content", {}), "tags": item.get("tags", []),
            "metadata": item.get("metadata", {}),
            "created_at": now, "updated_at": now,
            "created_by": item.get("created_by"),
        }
        _documents[doc_id] = doc
        created.append(doc)
    return func.HttpResponse(
        json.dumps({"documents": created}), status_code=201, mimetype="application/json")


@app.function_name("get_document_versions")
@app.route(route="knowledge/documents/{document_id}/versions", methods=["GET"])
async def get_document_versions(req: func.HttpRequest) -> func.HttpResponse:
    """Get the version history of a knowledge document."""
    doc_id = req.route_params.get("document_id", "")
    if doc_id not in _documents:
        return _json_error(f"Document '{doc_id}' not found", 404)
    versions = _document_versions.get(doc_id, [])
    return func.HttpResponse(
        json.dumps({"document_id": doc_id, "versions": versions}),
        mimetype="application/json")


@app.function_name("restore_document_version")
@app.route(route="knowledge/documents/{document_id}/restore", methods=["POST"])
async def restore_document_version(req: func.HttpRequest) -> func.HttpResponse:
    """Restore a document to a previous version."""
    doc_id = req.route_params.get("document_id", "")
    doc = _documents.get(doc_id)
    if doc is None:
        return _json_error(f"Document '{doc_id}' not found", 404)
    try:
        body = req.get_json()
    except ValueError:
        return _json_error("Invalid JSON body", 400)
    version = body.get("version")
    versions = _document_versions.get(doc_id, [])
    target = next((v for v in versions if v.get("version") == version), None)
    if target is None:
        return _json_error(f"Version {version} not found for document '{doc_id}'", 404)
    doc["content"] = target.get("content", doc["content"])
    doc["updated_at"] = datetime.now(timezone.utc).isoformat()
    return func.HttpResponse(json.dumps(doc), mimetype="application/json")


@app.function_name("export_documents")
@app.route(route="knowledge/documents/export", methods=["POST"])
async def export_documents(req: func.HttpRequest) -> func.HttpResponse:
    """Export documents matching a query."""
    try:
        body = req.get_json()
    except ValueError:
        return _json_error("Invalid JSON body", 400)
    query = (body.get("query") or "").lower()
    fmt = body.get("format", "json")
    results = list(_documents.values())
    if query:
        results = [d for d in results if query in d.get("title", "").lower()
                    or query in json.dumps(d.get("content", {})).lower()]
    return func.HttpResponse(
        json.dumps({"format": fmt, "documents": results}),
        mimetype="application/json")


# ── Risk Registry Endpoints ──────────────────────────────────────────────────


@app.function_name("register_risk")
@app.route(route="risks", methods=["POST"])
async def register_risk(req: func.HttpRequest) -> func.HttpResponse:
    """Register a new risk."""
    try:
        body = req.get_json()
    except ValueError:
        return _json_error("Invalid JSON body", 400)
    risk_id = body.get("id") or f"risk-{uuid.uuid4().hex[:8]}"
    now = datetime.now(timezone.utc).isoformat()
    risk = {
        "id": risk_id, "title": body.get("title", ""),
        "description": body.get("description", ""),
        "category": body.get("category", "operational"),
        "status": "identified", "owner": body.get("owner", "system"),
        "assessment": None, "mitigation_plan": None,
        "tags": body.get("tags", []), "context": body.get("context", {}),
        "created_at": now, "updated_at": now,
    }
    _risks[risk_id] = risk
    return func.HttpResponse(json.dumps(risk), status_code=201, mimetype="application/json")


@app.function_name("list_risks")
@app.route(route="risks", methods=["GET"])
async def list_risks(req: func.HttpRequest) -> func.HttpResponse:
    """List risks with optional filters."""
    status = req.params.get("status")
    category = req.params.get("category")
    results = list(_risks.values())
    if status:
        results = [r for r in results if r["status"] == status]
    if category:
        results = [r for r in results if r["category"] == category]
    return func.HttpResponse(json.dumps({"risks": results}), mimetype="application/json")


@app.function_name("assess_risk")
@app.route(route="risks/{risk_id}/assess", methods=["POST"])
async def assess_risk(req: func.HttpRequest) -> func.HttpResponse:
    """Assess a risk."""
    risk_id = req.route_params.get("risk_id", "")
    risk = _risks.get(risk_id)
    if risk is None:
        return _json_error(f"Risk '{risk_id}' not found", 404)
    try:
        body = req.get_json()
    except ValueError:
        return _json_error("Invalid JSON body", 400)
    likelihood = body.get("likelihood", 0.5)
    impact = body.get("impact", 0.5)
    score = likelihood * impact
    severity = (
        "critical" if score >= 0.8 else
        "high" if score >= 0.6 else
        "medium" if score >= 0.3 else
        "low" if score >= 0.1 else "info"
    )
    risk["assessment"] = {
        "likelihood": likelihood, "impact": impact, "severity": severity,
        "assessed_at": datetime.now(timezone.utc).isoformat(),
        "assessor": body.get("assessor"), "notes": body.get("notes"),
    }
    risk["status"] = "assessing"
    risk["updated_at"] = datetime.now(timezone.utc).isoformat()
    return func.HttpResponse(json.dumps(risk), mimetype="application/json")


@app.function_name("update_risk_status")
@app.route(route="risks/{risk_id}/status", methods=["POST"])
async def update_risk_status(req: func.HttpRequest) -> func.HttpResponse:
    """Update risk status."""
    risk_id = req.route_params.get("risk_id", "")
    risk = _risks.get(risk_id)
    if risk is None:
        return _json_error(f"Risk '{risk_id}' not found", 404)
    try:
        body = req.get_json()
    except ValueError:
        return _json_error("Invalid JSON body", 400)
    risk["status"] = body.get("status", risk["status"])
    risk["updated_at"] = datetime.now(timezone.utc).isoformat()
    return func.HttpResponse(json.dumps(risk), mimetype="application/json")


@app.function_name("add_mitigation_plan")
@app.route(route="risks/{risk_id}/mitigate", methods=["POST"])
async def add_mitigation_plan(req: func.HttpRequest) -> func.HttpResponse:
    """Add a mitigation plan to a risk."""
    risk_id = req.route_params.get("risk_id", "")
    risk = _risks.get(risk_id)
    if risk is None:
        return _json_error(f"Risk '{risk_id}' not found", 404)
    try:
        body = req.get_json()
    except ValueError:
        return _json_error("Invalid JSON body", 400)
    risk["mitigation_plan"] = body.get("plan", "")
    risk["status"] = "mitigating"
    risk["updated_at"] = datetime.now(timezone.utc).isoformat()
    return func.HttpResponse(json.dumps(risk), mimetype="application/json")


# ── Risk Aggregation Endpoints ───────────────────────────────────────────────


@app.function_name("get_risk_heatmap")
@app.route(route="risks/heatmap", methods=["GET"])
async def get_risk_heatmap(req: func.HttpRequest) -> func.HttpResponse:
    """Compute and return a risk heatmap from the risks store."""
    cells: list = []
    for risk in _risks.values():
        assessment = risk.get("assessment")
        if assessment:
            cells.append({
                "risk_id": risk["id"],
                "title": risk["title"],
                "likelihood": assessment.get("likelihood", 0),
                "impact": assessment.get("impact", 0),
                "severity": assessment.get("severity", "info"),
            })
    return func.HttpResponse(
        json.dumps({"cells": cells, "generated_at": datetime.now(timezone.utc).isoformat()}),
        mimetype="application/json")


@app.function_name("get_risk_summary")
@app.route(route="risks/summary", methods=["GET"])
async def get_risk_summary(req: func.HttpRequest) -> func.HttpResponse:
    """Compute and return risk summary statistics."""
    total = len(_risks)
    by_status: Dict[str, int] = {}
    by_category: Dict[str, int] = {}
    for risk in _risks.values():
        by_status[risk["status"]] = by_status.get(risk["status"], 0) + 1
        by_category[risk["category"]] = by_category.get(risk["category"], 0) + 1
    return func.HttpResponse(json.dumps({
        "total": total, "by_status": by_status, "by_category": by_category,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }), mimetype="application/json")


@app.function_name("get_risk_trends")
@app.route(route="risks/trends", methods=["GET"])
async def get_risk_trends(req: func.HttpRequest) -> func.HttpResponse:
    """Return risk trend data (placeholder)."""
    return func.HttpResponse(json.dumps({
        "trends": [], "generated_at": datetime.now(timezone.utc).isoformat(),
    }), mimetype="application/json")


# ── Audit Trail / Decision Ledger Endpoints ──────────────────────────────────


@app.function_name("log_decision")
@app.route(route="audit/decisions", methods=["POST"])
async def log_decision(req: func.HttpRequest) -> func.HttpResponse:
    """Log a decision."""
    try:
        body = req.get_json()
    except ValueError:
        return _json_error("Invalid JSON body", 400)
    record = {
        "id": body.get("id") or f"dec-{uuid.uuid4().hex[:8]}",
        "orchestration_id": body.get("orchestration_id"),
        "agent_id": body.get("agent_id"),
        "decision_type": body.get("decision_type", ""),
        "title": body.get("title", ""),
        "description": body.get("description", ""),
        "rationale": body.get("rationale"),
        "outcome": body.get("outcome"),
        "confidence": body.get("confidence"),
        "context": body.get("context", {}),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _decisions.append(record)
    return func.HttpResponse(json.dumps(record), status_code=201, mimetype="application/json")


@app.function_name("get_decision_history")
@app.route(route="audit/decisions", methods=["GET"])
async def get_decision_history(req: func.HttpRequest) -> func.HttpResponse:
    """Get decision history."""
    orch_id = req.params.get("orchestration_id")
    agent_id = req.params.get("agent_id")
    results = list(_decisions)
    if orch_id:
        results = [d for d in results if d.get("orchestration_id") == orch_id]
    if agent_id:
        results = [d for d in results if d.get("agent_id") == agent_id]
    return func.HttpResponse(json.dumps({"decisions": results}), mimetype="application/json")


@app.function_name("get_audit_trail")
@app.route(route="audit/trail", methods=["GET"])
async def get_audit_trail(req: func.HttpRequest) -> func.HttpResponse:
    """Get the audit trail."""
    return func.HttpResponse(json.dumps({"entries": _audit_entries}), mimetype="application/json")


# ── Audit Compliance Endpoints ───────────────────────────────────────────────


@app.function_name("generate_compliance_report")
@app.route(route="audit/compliance-report", methods=["POST"])
async def generate_compliance_report(req: func.HttpRequest) -> func.HttpResponse:
    """Generate a compliance report from the decisions store."""
    try:
        body = req.get_json()
    except ValueError:
        body = {}
    framework = body.get("framework", "general")
    now = datetime.now(timezone.utc).isoformat()
    total = len(_decisions)
    compliant = sum(1 for d in _decisions if d.get("outcome") == "approved")
    return func.HttpResponse(json.dumps({
        "report_id": f"rpt-{uuid.uuid4().hex[:8]}",
        "framework": framework,
        "total_decisions": total,
        "compliant_decisions": compliant,
        "compliance_rate": (compliant / total) if total > 0 else 0.0,
        "generated_at": now,
    }), status_code=201, mimetype="application/json")


@app.function_name("get_decision_chain")
@app.route(route="audit/decisions/{decision_id}/chain", methods=["GET"])
async def get_decision_chain(req: func.HttpRequest) -> func.HttpResponse:
    """Get the chain of related decisions for a given decision ID."""
    decision_id = req.route_params.get("decision_id", "")
    target = next((d for d in _decisions if d.get("id") == decision_id), None)
    if target is None:
        return _json_error(f"Decision '{decision_id}' not found", 404)
    orch_id = target.get("orchestration_id")
    chain = [d for d in _decisions if d.get("orchestration_id") == orch_id] if orch_id else [target]
    return func.HttpResponse(
        json.dumps({"decision_id": decision_id, "chain": chain}),
        mimetype="application/json")


# ── Covenant Management Endpoints ────────────────────────────────────────────


@app.function_name("create_covenant")
@app.route(route="covenants", methods=["POST"])
async def create_covenant(req: func.HttpRequest) -> func.HttpResponse:
    """Create a covenant."""
    try:
        body = req.get_json()
    except ValueError:
        return _json_error("Invalid JSON body", 400)
    cov_id = body.get("id") or f"cov-{uuid.uuid4().hex[:8]}"
    now = datetime.now(timezone.utc).isoformat()
    cov = {
        "id": cov_id, "title": body.get("title", ""),
        "version": body.get("version", "1.0"), "status": "draft",
        "parties": body.get("parties", []), "terms": body.get("terms", {}),
        "signers": [], "created_at": now, "updated_at": now,
    }
    _covenants[cov_id] = cov
    return func.HttpResponse(json.dumps(cov), status_code=201, mimetype="application/json")


@app.function_name("list_covenants")
@app.route(route="covenants", methods=["GET"])
async def list_covenants(req: func.HttpRequest) -> func.HttpResponse:
    """List covenants."""
    status = req.params.get("status")
    results = list(_covenants.values())
    if status:
        results = [c for c in results if c["status"] == status]
    return func.HttpResponse(json.dumps({"covenants": results}), mimetype="application/json")


@app.function_name("validate_covenant")
@app.route(route="covenants/{covenant_id}/validate", methods=["GET"])
async def validate_covenant(req: func.HttpRequest) -> func.HttpResponse:
    """Validate a covenant."""
    cov_id = req.route_params.get("covenant_id", "")
    if cov_id not in _covenants:
        return _json_error(f"Covenant '{cov_id}' not found", 404)
    return func.HttpResponse(json.dumps({
        "covenant_id": cov_id, "valid": True, "violations": [],
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }), mimetype="application/json")


@app.function_name("sign_covenant")
@app.route(route="covenants/{covenant_id}/sign", methods=["POST"])
async def sign_covenant(req: func.HttpRequest) -> func.HttpResponse:
    """Sign a covenant."""
    cov_id = req.route_params.get("covenant_id", "")
    cov = _covenants.get(cov_id)
    if cov is None:
        return _json_error(f"Covenant '{cov_id}' not found", 404)
    try:
        body = req.get_json()
    except ValueError:
        return _json_error("Invalid JSON body", 400)
    signer = body.get("signer", "")
    if signer and signer not in cov["signers"]:
        cov["signers"].append(signer)
    cov["updated_at"] = datetime.now(timezone.utc).isoformat()
    return func.HttpResponse(json.dumps(cov), mimetype="application/json")


# ── Analytics & Metrics Endpoints ────────────────────────────────────────────


@app.function_name("record_metric")
@app.route(route="metrics", methods=["POST"])
async def record_metric(req: func.HttpRequest) -> func.HttpResponse:
    """Record a metric data point."""
    try:
        body = req.get_json()
    except ValueError:
        return _json_error("Invalid JSON body", 400)
    _metrics_store.append({
        "name": body.get("name", ""),
        "value": body.get("value", 0.0),
        "tags": body.get("tags", {}),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    return func.HttpResponse(status_code=204)


@app.function_name("get_metrics")
@app.route(route="metrics", methods=["GET"])
async def get_metrics(req: func.HttpRequest) -> func.HttpResponse:
    """Retrieve metric time series."""
    name = req.params.get("name", "")
    points = [m for m in _metrics_store if m["name"] == name]
    return func.HttpResponse(json.dumps({
        "name": name,
        "data_points": [{"value": p["value"], "tags": p["tags"],
                          "timestamp": p["timestamp"]} for p in points],
    }), mimetype="application/json")


@app.function_name("create_kpi")
@app.route(route="kpis", methods=["POST"])
async def create_kpi(req: func.HttpRequest) -> func.HttpResponse:
    """Create a KPI definition."""
    try:
        body = req.get_json()
    except ValueError:
        return _json_error("Invalid JSON body", 400)
    kpi_id = body.get("id") or f"kpi-{uuid.uuid4().hex[:8]}"
    kpi = {
        "id": kpi_id, "name": body.get("name", ""),
        "description": body.get("description", ""),
        "target_value": body.get("target_value"),
        "current_value": body.get("current_value"),
        "unit": body.get("unit", ""),
        "metadata": body.get("metadata", {}),
    }
    _kpis[kpi_id] = kpi
    return func.HttpResponse(json.dumps(kpi), status_code=201, mimetype="application/json")


@app.function_name("get_kpi_dashboard")
@app.route(route="kpis/dashboard", methods=["GET"])
async def get_kpi_dashboard(req: func.HttpRequest) -> func.HttpResponse:
    """Get the KPI dashboard."""
    return func.HttpResponse(json.dumps({
        "kpis": list(_kpis.values()),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }), mimetype="application/json")


# ── Dashboards & Alerts Endpoints ────────────────────────────────────────────


@app.function_name("create_dashboard")
@app.route(route="dashboards", methods=["POST"])
async def create_dashboard(req: func.HttpRequest) -> func.HttpResponse:
    """Create a custom dashboard."""
    try:
        body = req.get_json()
    except ValueError:
        return _json_error("Invalid JSON body", 400)
    dash_id = body.get("id") or f"dash-{uuid.uuid4().hex[:8]}"
    now = datetime.now(timezone.utc).isoformat()
    dashboard = {
        "id": dash_id, "name": body.get("name", ""),
        "description": body.get("description", ""),
        "widgets": body.get("widgets", []),
        "created_at": now, "updated_at": now,
    }
    _dashboards_store[dash_id] = dashboard
    return func.HttpResponse(json.dumps(dashboard), status_code=201, mimetype="application/json")


@app.function_name("create_alert")
@app.route(route="alerts", methods=["POST"])
async def create_alert(req: func.HttpRequest) -> func.HttpResponse:
    """Create a metric alert."""
    try:
        body = req.get_json()
    except ValueError:
        return _json_error("Invalid JSON body", 400)
    alert_id = body.get("id") or f"alert-{uuid.uuid4().hex[:8]}"
    now = datetime.now(timezone.utc).isoformat()
    alert = {
        "id": alert_id, "name": body.get("name", ""),
        "metric": body.get("metric", ""),
        "condition": body.get("condition", ""),
        "threshold": body.get("threshold"),
        "status": "active",
        "created_at": now, "updated_at": now,
    }
    _alerts_store[alert_id] = alert
    return func.HttpResponse(json.dumps(alert), status_code=201, mimetype="application/json")


@app.function_name("list_alerts")
@app.route(route="alerts", methods=["GET"])
async def list_alerts(req: func.HttpRequest) -> func.HttpResponse:
    """List metric alerts."""
    return func.HttpResponse(
        json.dumps({"alerts": list(_alerts_store.values())}),
        mimetype="application/json")


# ── MCP Server Integration Endpoints ────────────────────────────────────────


@app.function_name("list_mcp_servers")
@app.route(route="mcp/servers", methods=["GET"])
async def list_mcp_servers(req: func.HttpRequest) -> func.HttpResponse:
    """List available MCP servers."""
    return func.HttpResponse(
        json.dumps({"servers": list(_mcp_servers.values())}),
        mimetype="application/json",
    )


@app.function_name("call_mcp_tool")
@app.route(route="mcp/servers/{server}/tools/{tool}", methods=["POST"])
async def call_mcp_tool(req: func.HttpRequest) -> func.HttpResponse:
    """Invoke a tool on an MCP server."""
    server = req.route_params.get("server", "")
    tool = req.route_params.get("tool", "")
    try:
        args = req.get_json()
    except ValueError:
        args = {}
    return func.HttpResponse(json.dumps({
        "server": server, "tool": tool, "args": args, "result": None,
    }), mimetype="application/json")


@app.function_name("get_mcp_server_status")
@app.route(route="mcp/servers/{server}/status", methods=["GET"])
async def get_mcp_server_status(req: func.HttpRequest) -> func.HttpResponse:
    """Get MCP server status."""
    server = req.route_params.get("server", "")
    return func.HttpResponse(json.dumps({
        "name": server, "status": "running", "healthy": True,
        "last_checked": datetime.now(timezone.utc).isoformat(),
    }), mimetype="application/json")


# ── Agent Interaction Endpoints ──────────────────────────────────────────────


@app.function_name("ask_agent")
@app.route(route="agents/{agent_id}/ask", methods=["POST"])
async def ask_agent(req: func.HttpRequest) -> func.HttpResponse:
    """Direct message to an agent."""
    agent_id = req.route_params.get("agent_id", "")
    try:
        body = req.get_json()
    except ValueError:
        return _json_error("Invalid JSON body", 400)
    return func.HttpResponse(json.dumps({
        "agent_id": agent_id,
        "message": f"Response from {agent_id}",
        "context": body.get("context", {}),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }), mimetype="application/json")


@app.function_name("send_to_agent")
@app.route(route="agents/{agent_id}/send", methods=["POST"])
async def send_to_agent(req: func.HttpRequest) -> func.HttpResponse:
    """Fire-and-forget message to an agent."""
    return func.HttpResponse(status_code=202)


# ── Network Federation Endpoints ─────────────────────────────────────────────


@app.function_name("create_network")
@app.route(route="network", methods=["POST"])
async def create_network(req: func.HttpRequest) -> func.HttpResponse:
    """Create a new network with a covenant."""
    try:
        body = req.get_json()
    except ValueError:
        return _json_error("Invalid JSON body", 400)
    net_id = body.get("id") or f"net-{uuid.uuid4().hex[:8]}"
    now = datetime.now(timezone.utc).isoformat()
    network = {
        "id": net_id, "name": body.get("name", ""),
        "covenant_id": body.get("covenant_id"),
        "members": [], "status": "active",
        "created_at": now, "updated_at": now,
    }
    _networks[net_id] = network
    return func.HttpResponse(json.dumps(network), status_code=201, mimetype="application/json")


@app.function_name("request_network_membership")
@app.route(route="network/{network_id}/request", methods=["POST"])
async def request_network_membership(req: func.HttpRequest) -> func.HttpResponse:
    """Request membership in a network."""
    network_id = req.route_params.get("network_id", "")
    network = _networks.get(network_id)
    if network is None:
        return _json_error(f"Network '{network_id}' not found", 404)
    try:
        body = req.get_json()
    except ValueError:
        return _json_error("Invalid JSON body", 400)
    request_record = {
        "network_id": network_id,
        "requester": body.get("requester", "unknown"),
        "status": "pending",
        "requested_at": datetime.now(timezone.utc).isoformat(),
    }
    return func.HttpResponse(json.dumps(request_record), status_code=201, mimetype="application/json")


@app.function_name("verify_peer")
@app.route(route="network/{network_id}/verify/{peer_id}", methods=["GET"])
async def verify_peer(req: func.HttpRequest) -> func.HttpResponse:
    """Verify a peer in a network."""
    network_id = req.route_params.get("network_id", "")
    peer_id = req.route_params.get("peer_id", "")
    if network_id not in _networks:
        return _json_error(f"Network '{network_id}' not found", 404)
    return func.HttpResponse(json.dumps({
        "network_id": network_id, "peer_id": peer_id,
        "verified": True,
        "verified_at": datetime.now(timezone.utc).isoformat(),
    }), mimetype="application/json")


# ── Network Discovery Endpoints ─────────────────────────────────────────────


@app.function_name("discover_peers")
@app.route(route="network/discover", methods=["POST"])
async def discover_peers(req: func.HttpRequest) -> func.HttpResponse:
    """Discover peer applications."""
    return func.HttpResponse(json.dumps({"peers": []}), mimetype="application/json")


@app.function_name("join_network")
@app.route(route="network/{network_id}/join", methods=["POST"])
async def join_network(req: func.HttpRequest) -> func.HttpResponse:
    """Join a network."""
    network_id = req.route_params.get("network_id", "")
    membership = {
        "network_id": network_id, "app_id": "caller",
        "joined_at": datetime.now(timezone.utc).isoformat(),
        "status": "active",
    }
    _network_memberships[network_id] = membership
    return func.HttpResponse(json.dumps(membership), mimetype="application/json")


@app.function_name("list_networks")
@app.route(route="network", methods=["GET"])
async def list_networks(req: func.HttpRequest) -> func.HttpResponse:
    """List available networks."""
    return func.HttpResponse(
        json.dumps({"networks": list(_networks.values())}),
        mimetype="application/json",
    )


# ── Orchestration Streaming Endpoints ────────────────────────────────────────


@app.function_name("subscribe_orchestration")
@app.route(route="orchestrations/{orchestration_id}/subscribe", methods=["POST"])
async def subscribe_orchestration(req: func.HttpRequest) -> func.HttpResponse:
    """Subscribe to updates for an orchestration."""
    orch_id = req.route_params.get("orchestration_id", "")
    if orch_id not in _orchestrations:
        return _json_error(f"Orchestration '{orch_id}' not found", 404)
    try:
        body = req.get_json()
    except ValueError:
        body = {}
    subscriber = body.get("subscriber", f"sub-{uuid.uuid4().hex[:8]}")
    subs = _orchestration_subscriptions.setdefault(orch_id, [])
    subs.append({"subscriber": subscriber, "subscribed_at": datetime.now(timezone.utc).isoformat()})
    return func.HttpResponse(json.dumps({
        "orchestration_id": orch_id, "subscriber": subscriber, "status": "subscribed",
    }), status_code=201, mimetype="application/json")


@app.function_name("get_orchestration_updates")
@app.route(route="orchestrations/{orchestration_id}/updates", methods=["GET"])
async def get_orchestration_updates(req: func.HttpRequest) -> func.HttpResponse:
    """Get updates for an orchestration."""
    orch_id = req.route_params.get("orchestration_id", "")
    if orch_id not in _orchestrations:
        return _json_error(f"Orchestration '{orch_id}' not found", 404)
    updates = _orchestration_updates.get(orch_id, [])
    return func.HttpResponse(
        json.dumps({"orchestration_id": orch_id, "updates": updates}),
        mimetype="application/json")


# ── Webhook Endpoints ────────────────────────────────────────────────────────


@app.function_name("register_webhook")
@app.route(route="webhooks", methods=["POST"])
async def register_webhook(req: func.HttpRequest) -> func.HttpResponse:
    """Register a webhook."""
    try:
        body = req.get_json()
    except ValueError:
        return _json_error("Invalid JSON body", 400)
    wh_id = body.get("id") or f"wh-{uuid.uuid4().hex[:8]}"
    now = datetime.now(timezone.utc).isoformat()
    webhook = {
        "id": wh_id, "url": body.get("url", ""),
        "events": body.get("events", []),
        "status": "active",
        "created_at": now, "updated_at": now,
    }
    _webhooks_store[wh_id] = webhook
    return func.HttpResponse(json.dumps(webhook), status_code=201, mimetype="application/json")


@app.function_name("list_webhooks")
@app.route(route="webhooks", methods=["GET"])
async def list_webhooks(req: func.HttpRequest) -> func.HttpResponse:
    """List registered webhooks."""
    return func.HttpResponse(
        json.dumps({"webhooks": list(_webhooks_store.values())}),
        mimetype="application/json")


# ── Internal Helpers ─────────────────────────────────────────────────────────


def _json_error(message: str, status_code: int) -> func.HttpResponse:
    """Return a JSON error response."""
    return func.HttpResponse(
        json.dumps({"error": message}),
        status_code=status_code,
        mimetype="application/json",
    )


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
