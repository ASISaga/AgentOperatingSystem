# AgentOperatingSystem Examples

This directory contains examples demonstrating how to use the AgentOperatingSystem platform infrastructure.

## Platform Integration Example

**File**: `platform_integration_example.py`

Demonstrates a complete decision workflow using all major platform components:

### Components Demonstrated

1. **Platform Contracts** (`platform/`)
   - Message envelopes with correlation/causation IDs
   - Event definitions (DecisionRequested, DecisionApproved)
   - Command/Query contracts

2. **Reliability Patterns** (`reliability/`)
   - Idempotent processing with deduplication
   - Retry logic with exponential backoff
   - Circuit breakers for dependency protection
   - State machines for workflow management

3. **Governance** (`governance/`)
   - Tamper-evident audit logging with hash chains
   - Compliance assertions (SOC2, ISO 27001)
   - Risk registry with assessment
   - Decision rationales with precedent linking

4. **Observability** (`observability/`)
   - Metrics collection (latency, SLA compliance)
   - Distributed tracing with correlation IDs
   - Structured logging with redaction
   - Alerting system with threshold monitoring

5. **Knowledge Services** (`knowledge/`)
   - Evidence retrieval
   - Document indexing
   - Precedent query and similarity matching

### Running the Example

```bash
# From the repository root
# Set PYTHONPATH to include src directory
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"

# Run the example
python examples/platform_integration_example.py
```

### Expected Output

The example will:
1. Initialize all platform components
2. Create a budget approval decision request
3. Process it through the full governance workflow
4. Record comprehensive audit trail
5. Assess risks and compliance
6. Search for precedent decisions
7. Track metrics and generate alerts
8. Print a summary of the entire workflow

### Integration with BusinessInfinity

These platform components are designed to be consumed by BusinessInfinity and other agent-based applications:

```python
# Example BusinessInfinity integration
from AgentOperatingSystem.platform import MessageEnvelope, CommandContract
from AgentOperatingSystem.reliability import IdempotencyHandler, CircuitBreaker
from AgentOperatingSystem.governance import AuditLogger, ComplianceEngine
from AgentOperatingSystem.observability import MetricsCollector, StructuredLogger

class BusinessWorkflow:
    def __init__(self):
        # Use AOS infrastructure
        self.audit = AuditLogger()
        self.compliance = ComplianceEngine()
        self.metrics = MetricsCollector()
        self.logger = StructuredLogger()
        self.idempotency = IdempotencyHandler()
```

## More Examples

Additional examples will be added to demonstrate:
- Chaos testing scenarios
- Multi-agent coordination
- Event-driven workflows
- Plugin framework usage

## Azure Foundry Agent Service Example

**File**: `foundry_agent_service_example.py`

Demonstrates how to use Microsoft Azure Foundry Agent Service with Llama 3.3 70B as the core reasoning engine.

### Features Demonstrated

1. **Basic Message Sending**
   - Simple request/response with Llama 3.3 70B
   - Configuration from environment variables
   - Response handling and metrics

2. **Stateful Threads**
   - Creating persistent conversation threads
   - Multi-turn conversations with context preservation
   - Thread metadata and management
   - Thread lifecycle (create, use, delete)

3. **Entra Agent ID**
   - Secure agent identity management
   - Integration with Microsoft Entra ID
   - Agent-level access control

4. **Foundry Tools**
   - Accessing Azure AI Foundry tools
   - Tool selection and usage
   - Custom tool integration

5. **Model Orchestrator Integration**
   - Using Foundry Agent Service through ModelOrchestrator
   - Automatic model selection
   - Request routing and management

6. **Metrics and Monitoring**
   - Request tracking
   - Token usage monitoring
   - Health checks
   - Performance metrics

### Prerequisites

Set up the following environment variables:

```bash
export FOUNDRY_AGENT_SERVICE_ENDPOINT="https://your-endpoint.azure.com"
export FOUNDRY_AGENT_SERVICE_API_KEY="your-api-key"
export FOUNDRY_AGENT_ID="your-agent-id"  # Optional
```

### Running the Example

```bash
# From the repository root
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"

# Run the example
python examples/foundry_agent_service_example.py
```

### Expected Output

The example will demonstrate:
1. Basic message sending with Llama 3.3 70B
2. Creating and managing stateful threads
3. Multi-turn conversations with context preservation
4. Using Foundry Tools for enhanced capabilities
5. Integration with Model Orchestrator
6. Advanced configuration options
7. Metrics collection and health monitoring

### Documentation

For complete documentation, see [docs/FOUNDRY_AGENT_SERVICE.md](../docs/FOUNDRY_AGENT_SERVICE.md)
