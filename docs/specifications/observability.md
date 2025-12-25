# Technical Specification: Observability System

**Document Version:** 2025.1.2  
**Status:** Implemented  
**Date:** December 25, 2025  
**Module:** AgentOperatingSystem Observability (`src/AgentOperatingSystem/observability/`)

---

## 1. System Overview

The AOS Observability System provides comprehensive monitoring, logging, metrics collection, alerting, and tracing capabilities for the entire Agent Operating System. It enables deep visibility into system behavior, performance, and health.

**Key Components:**
- **Metrics** (`metrics.py`): Performance and operational metrics
- **Logging** (`logging.py`): Structured logging infrastructure
- **Tracing** (`tracing.py`): Distributed request tracing
- **Alerting** (`alerting.py`): Alert management and notification

---

## 2. Metrics System

### 2.1 Metrics Collection

```python
from AgentOperatingSystem.observability.metrics import MetricsCollector, MetricType

# Initialize metrics collector
metrics = MetricsCollector(retention_hours=24)

# Counter metric
metrics.increment("agent.tasks.completed", tags={"agent": "ceo"})

# Gauge metric
metrics.gauge("agent.queue.depth", 42, tags={"agent": "cfo"})

# Histogram metric
metrics.timing("agent.response_time_ms", 125.5, tags={"agent": "cmo"})

# Summary metric
metrics.summary("agent.task_duration", 3600, tags={"agent": "coo"})
```

### 2.2 Metric Types

**Counter:**
- Monotonically increasing value
- Examples: request count, error count, tasks completed
```python
metrics.increment("http.requests.total")
metrics.increment("errors.validation", value=5)
```

**Gauge:**
- Point-in-time value that can go up or down
- Examples: queue depth, active connections, memory usage
```python
metrics.gauge("system.memory.used_mb", 4096)
metrics.gauge("agent.active_tasks", 7)
```

**Histogram:**
- Distribution of values over time
- Examples: response times, request sizes
```python
metrics.histogram("api.latency_ms", 42.5)
metrics.histogram("message.size_bytes", 1024)
```

**Summary:**
- Percentile calculations
- Examples: p50, p95, p99 latencies
```python
metrics.summary("task.duration_seconds", 125.3)
```

### 2.3 Tracked Metrics

**Decision Latency:**
```python
import time

start = time.time()
decision = await agent.make_decision(context)
duration_ms = (time.time() - start) * 1000

metrics.timing("decision.latency_ms", duration_ms, tags={
    "agent": agent_id,
    "decision_type": decision.type
})
```

**SLA Compliance:**
```python
# Track SLA compliance
sla_target_ms = 1000
actual_ms = 850

is_compliant = actual_ms <= sla_target_ms
metrics.increment("sla.requests.total")
if is_compliant:
    metrics.increment("sla.requests.compliant")

compliance_rate = metrics.get_rate("sla.requests.compliant", "sla.requests.total")
```

**Incident MTTR:**
```python
# Mean Time To Resolution
incident_start = datetime.now()
# ... incident handling ...
incident_end = datetime.now()

mttr_seconds = (incident_end - incident_start).total_seconds()
metrics.summary("incident.mttr_seconds", mttr_seconds, tags={
    "severity": incident.severity,
    "category": incident.category
})
```

### 2.4 Metric Queries

```python
# Get percentiles
p50 = metrics.get_percentile("api.latency_ms", 50)
p95 = metrics.get_percentile("api.latency_ms", 95)
p99 = metrics.get_percentile("api.latency_ms", 99)

# Get aggregations
total_requests = metrics.get_count("http.requests.total")
avg_latency = metrics.get_average("api.latency_ms", window_minutes=5)

# Get metrics by tags
ceo_metrics = metrics.query(
    metric_name="agent.tasks.completed",
    tags={"agent": "ceo"},
    start_time=start,
    end_time=end
)
```

---

## 3. Logging System

### 3.1 Structured Logging

```python
from AgentOperatingSystem.observability.logging import StructuredLogger

# Initialize logger
logger = StructuredLogger(
    name="AOS.Agent.CEO",
    level="INFO",
    format="json"
)

# Log with structured data
logger.info(
    "Task completed successfully",
    extra={
        "task_id": "task_001",
        "agent_id": "ceo_agent",
        "duration_ms": 1250,
        "result_summary": "Analysis completed",
        "tags": ["strategy", "quarterly"]
    }
)

# Log levels
logger.debug("Debug information", extra={"details": debug_info})
logger.info("Informational message", extra={"context": context})
logger.warning("Warning message", extra={"issue": issue_details})
logger.error("Error occurred", extra={"error": str(e), "traceback": tb})
logger.critical("Critical failure", extra={"failure": failure_details})
```

### 3.2 Log Correlation

```python
# Add correlation ID
logger = logger.with_context({
    "correlation_id": "corr_12345",
    "request_id": "req_67890",
    "user_id": "user_001"
})

# All subsequent logs include correlation context
logger.info("Processing request")
# Output includes correlation_id, request_id, user_id
```

### 3.3 Log Aggregation

```python
# Query logs
logs = logger.query(
    level="ERROR",
    start_time=datetime.now() - timedelta(hours=1),
    filters={"agent_id": "ceo_agent"}
)

# Analyze error patterns
error_summary = logger.analyze_errors(
    time_window=timedelta(hours=24),
    group_by="error_type"
)
```

### 3.4 Log Shipping

```python
# Configure log shipping to external systems
logger.configure_shipping(
    destinations=[
        {
            "type": "azure_log_analytics",
            "workspace_id": os.getenv("LOG_ANALYTICS_WORKSPACE_ID"),
            "key": os.getenv("LOG_ANALYTICS_KEY")
        },
        {
            "type": "elasticsearch",
            "endpoint": "https://elasticsearch:9200",
            "index": "aos-logs"
        }
    ]
)
```

---

## 4. Distributed Tracing

### 4.1 Trace Creation

```python
from AgentOperatingSystem.observability.tracing import Tracer, Span

tracer = Tracer(service_name="aos_orchestrator")

# Create trace
with tracer.start_span("execute_workflow") as span:
    span.set_attribute("workflow_id", workflow_id)
    span.set_attribute("agent_count", len(agents))
    
    # Child span
    with tracer.start_span("validate_input", parent=span) as child_span:
        await validate_workflow_input(workflow_data)
    
    # Another child span
    with tracer.start_span("execute_steps", parent=span) as child_span:
        await execute_workflow_steps(workflow_id)
```

### 4.2 Cross-Service Tracing

```python
# Propagate trace context across services
trace_context = span.get_context()

# Send to another service
await http_client.post(
    "https://agent-service/execute",
    headers={
        "X-Trace-Context": trace_context.serialize()
    },
    json=task_data
)

# Receiving service continues the trace
incoming_context = request.headers.get("X-Trace-Context")
with tracer.continue_span(incoming_context) as span:
    await process_task(task_data)
```

### 4.3 Trace Analysis

```python
# Query traces
traces = tracer.query_traces(
    service="aos_orchestrator",
    operation="execute_workflow",
    min_duration_ms=1000,
    start_time=start,
    end_time=end
)

# Analyze trace
for trace in traces:
    print(f"Duration: {trace.duration_ms}ms")
    print(f"Spans: {len(trace.spans)}")
    print(f"Errors: {trace.error_count}")
```

---

## 5. Alerting System

### 5.1 Alert Definition

```python
from AgentOperatingSystem.observability.alerting import AlertManager, Alert, AlertSeverity

alert_manager = AlertManager()

# Define alert
alert = Alert(
    alert_id="high_error_rate",
    name="High Error Rate Detected",
    description="Error rate exceeded threshold",
    severity=AlertSeverity.HIGH,
    condition={
        "metric": "errors.total",
        "aggregation": "rate",
        "window": "5m",
        "threshold": 0.05,  # 5% error rate
        "operator": ">"
    },
    actions=[
        {"type": "email", "recipients": ["ops@example.com"]},
        {"type": "slack", "channel": "#alerts"},
        {"type": "pagerduty", "service_key": "..."}
    ]
)

await alert_manager.register_alert(alert)
```

### 5.2 Alert Severities

```python
class AlertSeverity(Enum):
    INFO = "info"           # Informational
    WARNING = "warning"     # Warning, no immediate action
    HIGH = "high"          # Requires attention
    CRITICAL = "critical"   # Requires immediate action
```

### 5.3 Alert Evaluation

```python
# Evaluate alerts
await alert_manager.evaluate_alerts()

# Manually trigger alert
await alert_manager.trigger_alert(
    alert_id="high_error_rate",
    context={
        "current_error_rate": 0.08,
        "threshold": 0.05,
        "affected_service": "agent_executor"
    }
)

# Acknowledge alert
await alert_manager.acknowledge_alert(
    alert_id="high_error_rate",
    acknowledged_by="ops_engineer"
)

# Resolve alert
await alert_manager.resolve_alert(
    alert_id="high_error_rate",
    resolution="Error rate returned to normal after deployment rollback"
)
```

### 5.4 Alert Routing

```python
# Define alert routing rules
alert_manager.add_routing_rule(
    severity=AlertSeverity.CRITICAL,
    route_to=["pagerduty", "sms"],
    escalation_minutes=15
)

alert_manager.add_routing_rule(
    severity=AlertSeverity.HIGH,
    route_to=["email", "slack"],
    escalation_minutes=60
)
```

---

## 6. Health Checks

### 6.1 Component Health

```python
from AgentOperatingSystem.observability.health import HealthChecker

health_checker = HealthChecker()

# Register health check
@health_checker.register("database")
async def check_database_health():
    try:
        await db.execute("SELECT 1")
        return {"status": "healthy", "latency_ms": 5}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

# Get overall health
health_status = await health_checker.get_health()
# {
#   "status": "healthy",
#   "components": {
#     "database": {"status": "healthy", "latency_ms": 5},
#     "message_bus": {"status": "healthy"},
#     "storage": {"status": "healthy"}
#   }
# }
```

### 6.2 Readiness and Liveness

```python
# Liveness: Is the service running?
@app.route("/health/live")
async def liveness():
    return {"status": "alive"}

# Readiness: Can the service accept traffic?
@app.route("/health/ready")
async def readiness():
    is_ready = await health_checker.is_ready()
    if is_ready:
        return {"status": "ready"}, 200
    else:
        return {"status": "not_ready"}, 503
```

---

## 7. Dashboards and Visualization

### 7.1 System Dashboard

**Key Metrics:**
- Request rate and latency (p50, p95, p99)
- Error rate and count
- Agent task throughput
- Resource utilization (CPU, memory)
- Queue depths

**Example Dashboard Configuration:**
```json
{
  "name": "AOS System Overview",
  "panels": [
    {
      "title": "Request Latency",
      "metric": "api.latency_ms",
      "visualization": "line",
      "aggregation": "percentile",
      "percentiles": [50, 95, 99]
    },
    {
      "title": "Error Rate",
      "metric": "errors.total",
      "visualization": "line",
      "aggregation": "rate",
      "window": "5m"
    },
    {
      "title": "Active Agents",
      "metric": "agent.active_count",
      "visualization": "gauge",
      "aggregation": "last"
    }
  ]
}
```

---

## 8. Integration Examples

### 8.1 With Azure Monitor

```python
from azure.monitor.opentelemetry import configure_azure_monitor

# Configure Azure Monitor integration
configure_azure_monitor(
    connection_string=os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
)

# Metrics automatically sent to Azure Monitor
metrics.increment("custom.metric")
```

### 8.2 With Prometheus

```python
from prometheus_client import Counter, Histogram, Gauge

# Export metrics for Prometheus
prom_counter = Counter("aos_tasks_total", "Total tasks", ["agent", "status"])
prom_histogram = Histogram("aos_latency_seconds", "Latency", ["operation"])

# Update metrics
prom_counter.labels(agent="ceo", status="completed").inc()
prom_histogram.labels(operation="decision").observe(1.25)
```

---

## 9. Best Practices

### 9.1 Metrics
1. **Use appropriate metric types** for different measurements
2. **Add meaningful tags** for filtering and grouping
3. **Set retention policies** to manage storage
4. **Track business metrics** alongside technical metrics
5. **Monitor metric cardinality** to avoid explosion

### 9.2 Logging
1. **Use structured logging** for better searchability
2. **Include correlation IDs** for distributed tracing
3. **Log at appropriate levels** (avoid log spam)
4. **Sanitize sensitive data** before logging
5. **Aggregate logs centrally** for analysis

### 9.3 Alerting
1. **Define clear alert conditions** and thresholds
2. **Avoid alert fatigue** with proper tuning
3. **Implement alert routing** based on severity
4. **Document runbooks** for alert response
5. **Review and update alerts** regularly

---

**Document Approval:**
- **Status:** Implemented and Active
- **Last Updated:** December 25, 2025
- **Owner:** AOS Observability Team
