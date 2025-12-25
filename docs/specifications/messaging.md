# Technical Specification: Messaging and Communication System

**Document Version:** 2025.1.2  
**Status:** Implemented  
**Date:** December 25, 2025  
**Module:** AgentOperatingSystem Messaging (`src/AgentOperatingSystem/messaging/`)

---

## 1. System Overview

The AOS Messaging System provides a comprehensive communication infrastructure for agent-to-agent (A2A) communication, inter-service messaging, and event-driven architectures. It enables asynchronous, reliable, and scalable communication across the entire Agent Operating System ecosystem.

**Key Features:**
- Central message bus for all AOS communications
- Agent-to-agent messaging with routing
- Event publishing and subscription
- Message queuing and delivery guarantees
- Conversation management and history
- Azure Service Bus integration
- Network protocol support for distributed agents

---

## 2. Architecture

### 2.1 Core Components

**MessageBus (`bus.py`)**
- Central message routing and delivery
- Subscription management
- Message queuing per agent
- Event processing loop

**ConversationSystem (`conversation_system.py`)**
- Multi-turn conversation management
- Context preservation across messages
- Conversation history and replay
- Participant tracking

**NetworkProtocol (`network_protocol.py`)**
- Agent-to-agent network communication
- Distributed agent discovery
- Message serialization and transport
- Connection pooling

**ServiceBusManager (`servicebus_manager.py`)**
- Azure Service Bus integration
- Topic and subscription management
- Message publishing to cloud
- Distributed event handling

**MessageRouter (`router.py`)**
- Intelligent message routing
- Priority-based delivery
- Load balancing across agents
- Routing rules and policies

**Message Types (`types.py`)**
- Standardized message structures
- Message priorities and types
- Metadata and headers

### 2.2 Communication Patterns

```
┌──────────────────────────────────────────────────────────┐
│                  Application Layer                       │
│              (Agents, Orchestrators)                     │
└────────────────────┬─────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────┐
│                   MessageBus                             │
│  ┌────────────┐  ┌────────────┐  ┌──────────────┐      │
│  │ Subscriber │  │  Publisher │  │ Queue Manager│      │
│  └────────────┘  └────────────┘  └──────────────┘      │
└────────────────────┬─────────────────────────────────────┘
                     │
        ┌────────────┼────────────┬──────────────┐
        │            │            │              │
        ▼            ▼            ▼              ▼
┌─────────────┐ ┌─────────┐ ┌──────────┐ ┌──────────────┐
│Conversation │ │ Network │ │ Service  │ │  Router      │
│   System    │ │Protocol │ │   Bus    │ │              │
└─────────────┘ └─────────┘ └──────────┘ └──────────────┘
```

---

## 3. Implementation Details

### 3.1 MessageBus Class

**Initialization:**
```python
from AgentOperatingSystem.messaging.bus import MessageBus
from AgentOperatingSystem.config.messagebus import MessageBusConfig

config = MessageBusConfig(
    enable_persistence=True,
    max_queue_size=1000,
    message_ttl_seconds=3600
)

message_bus = MessageBus(config)
await message_bus.start()
```

**Core Operations:**

**1. Publishing Messages:**
```python
from AgentOperatingSystem.messaging.types import Message, MessageType, MessagePriority

# Publish a message
message = Message(
    message_id="msg_001",
    message_type=MessageType.TASK,
    sender_id="orchestrator",
    recipient_id="ceo_agent",
    content={
        "task": "analyze_quarterly_report",
        "data": {"quarter": "Q2", "year": 2025}
    },
    priority=MessagePriority.HIGH,
    metadata={"correlation_id": "task_123"}
)

await message_bus.publish(message)
```

**2. Subscribing to Messages:**
```python
# Subscribe agent to receive messages
async def message_handler(message: Message):
    print(f"Received message: {message.content}")
    # Process message
    await process_message(message)

await message_bus.subscribe(
    agent_id="ceo_agent",
    message_types=[MessageType.TASK, MessageType.QUERY],
    handler=message_handler
)
```

**3. Message Queuing:**
```python
# Get messages for specific agent
messages = await message_bus.get_messages("ceo_agent", limit=10)

for message in messages:
    await process_message(message)
    await message_bus.acknowledge(message.message_id)
```

**4. Request-Response Pattern:**
```python
# Send request and wait for response
response = await message_bus.request(
    sender_id="orchestrator",
    recipient_id="cfo_agent",
    content={"query": "What's the Q2 revenue?"},
    timeout=30
)

print(f"Response: {response.content}")
```

### 3.2 Message Types and Structure

**Message Class:**
```python
@dataclass
class Message:
    message_id: str
    message_type: MessageType
    sender_id: str
    recipient_id: str
    content: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    priority: MessagePriority = MessagePriority.NORMAL
    metadata: Dict[str, Any] = field(default_factory=dict)
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    ttl: Optional[int] = None
```

**Message Types:**
```python
class MessageType(Enum):
    TASK = "task"                    # Task assignment
    QUERY = "query"                  # Information request
    RESPONSE = "response"            # Response to query
    EVENT = "event"                  # Event notification
    COMMAND = "command"              # Direct command
    STATUS = "status"                # Status update
    NOTIFICATION = "notification"    # General notification
    ERROR = "error"                  # Error message
```

**Message Priorities:**
```python
class MessagePriority(Enum):
    CRITICAL = 0    # Immediate processing
    HIGH = 1        # High priority
    NORMAL = 2      # Normal priority
    LOW = 3         # Low priority
    BACKGROUND = 4  # Background processing
```

### 3.3 Conversation System

**Managing Conversations:**
```python
from AgentOperatingSystem.messaging.conversation_system import ConversationSystem

conversation_system = ConversationSystem(storage_manager)

# Start a new conversation
conversation_id = await conversation_system.start_conversation(
    participants=["ceo_agent", "cfo_agent"],
    topic="quarterly_planning",
    metadata={"quarter": "Q2", "year": 2025}
)

# Add message to conversation
await conversation_system.add_message(
    conversation_id=conversation_id,
    sender_id="ceo_agent",
    content="What's our revenue projection for Q2?",
    message_type=MessageType.QUERY
)

# Get conversation history
history = await conversation_system.get_conversation_history(conversation_id)

# End conversation
await conversation_system.end_conversation(conversation_id)
```

**Conversation Context:**
```python
# Get conversation context for AI models
context = await conversation_system.get_context(
    conversation_id=conversation_id,
    max_messages=20
)

# Context includes:
# - Recent messages
# - Participants
# - Topic and metadata
# - Conversation state
```

### 3.4 Network Protocol

**Agent-to-Agent Communication:**
```python
from AgentOperatingSystem.messaging.network_protocol import NetworkProtocol

protocol = NetworkProtocol(config)

# Register agent on network
await protocol.register_agent(
    agent_id="ceo_agent",
    address="http://ceo-service:8080",
    capabilities=["strategy", "decision_making"]
)

# Send message to remote agent
await protocol.send_message(
    sender_id="local_agent",
    recipient_id="remote_agent",
    message=message_data
)

# Discover available agents
agents = await protocol.discover_agents(
    capabilities=["financial_analysis"]
)
```

**Connection Management:**
```python
# Establish persistent connection
connection = await protocol.connect(
    agent_id="remote_agent",
    address="http://remote-service:8080"
)

# Send via connection
await connection.send(message)

# Close connection
await connection.close()
```

### 3.5 Azure Service Bus Integration

**Service Bus Manager:**
```python
from AgentOperatingSystem.messaging.servicebus_manager import ServiceBusManager

# Initialize with connection string
service_bus = ServiceBusManager(
    connection_string=os.getenv("AZURE_SERVICE_BUS_CONNECTION_STRING")
)

# Send message to topic
await service_bus.send_to_topic(
    topic_name="agent_events",
    message={
        "event_type": "task_completed",
        "agent_id": "ceo_agent",
        "task_id": "task_001"
    }
)

# Receive messages from subscription
async for message in service_bus.receive_from_subscription(
    topic_name="agent_events",
    subscription_name="orchestrator_subscription"
):
    await process_event(message)
    await service_bus.complete_message(message)
```

**Topic and Subscription Management:**
```python
# Create topic
await service_bus.create_topic(
    topic_name="agent_tasks",
    max_size_in_mb=1024,
    default_message_ttl_seconds=3600
)

# Create subscription
await service_bus.create_subscription(
    topic_name="agent_tasks",
    subscription_name="ceo_agent_tasks",
    filter_rule="agent_id = 'ceo_agent'"
)
```

### 3.6 Message Router

**Routing Configuration:**
```python
from AgentOperatingSystem.messaging.router import MessageRouter

router = MessageRouter()

# Add routing rule
router.add_rule(
    name="high_priority_to_ceo",
    condition=lambda msg: msg.priority == MessagePriority.HIGH,
    target="ceo_agent"
)

# Add load balancing rule
router.add_load_balancing_rule(
    name="analysis_tasks",
    condition=lambda msg: msg.content.get("task_type") == "analysis",
    targets=["analyst_1", "analyst_2", "analyst_3"],
    strategy="round_robin"
)

# Route message
target_agent = router.route(message)
```

---

## 4. Communication Patterns

### 4.1 Publish-Subscribe Pattern

```python
# Publisher
await message_bus.publish(
    message_type=MessageType.EVENT,
    content={"event": "quarterly_report_ready"}
)

# Subscribers automatically receive the message
# Multiple subscribers can listen to the same event
```

### 4.2 Request-Response Pattern

```python
# Request
response = await message_bus.request(
    recipient_id="cfo_agent",
    content={"query": "revenue_forecast"},
    timeout=30
)

# Response is automatically correlated
print(response.content)
```

### 4.3 Command Pattern

```python
# Send command
await message_bus.send_command(
    recipient_id="agent_id",
    command="execute_task",
    parameters={"task_id": "task_001"}
)

# Agent executes command and optionally sends status updates
```

### 4.4 Event Streaming

```python
# Stream events
async for event in message_bus.stream_events(
    event_types=["task_completed", "agent_status_changed"]
):
    await handle_event(event)
```

---

## 5. Message Delivery Guarantees

### 5.1 At-Least-Once Delivery

```python
# Message is delivered at least once
# Requires explicit acknowledgment
message = await message_bus.receive("agent_id")
try:
    await process_message(message)
    await message_bus.acknowledge(message.message_id)
except Exception as e:
    # Message will be redelivered
    await message_bus.nack(message.message_id)
```

### 5.2 At-Most-Once Delivery

```python
# Message is delivered at most once
# No acknowledgment required
# Faster but less reliable
await message_bus.publish(
    message=message,
    delivery_mode="at_most_once"
)
```

### 5.3 Exactly-Once Delivery

```python
# Message is delivered exactly once
# Uses deduplication and idempotency
await message_bus.publish(
    message=message,
    delivery_mode="exactly_once",
    idempotency_key=f"task_{task_id}"
)
```

---

## 6. Error Handling and Resilience

### 6.1 Message Retry

```python
# Automatic retry with exponential backoff
await message_bus.publish(
    message=message,
    retry_policy={
        "max_attempts": 3,
        "backoff_multiplier": 2,
        "initial_delay": 1
    }
)
```

### 6.2 Dead Letter Queue

```python
# Messages that fail after max retries go to DLQ
dlq_messages = await message_bus.get_dead_letter_messages("ceo_agent")

for message in dlq_messages:
    # Analyze failure
    logger.error(f"Failed message: {message}")
    
    # Optionally reprocess
    if is_retryable(message):
        await message_bus.resubmit(message)
```

### 6.3 Circuit Breaker Integration

```python
from AgentOperatingSystem.reliability.circuit_breaker import CircuitBreaker

circuit = CircuitBreaker(name="message_delivery")

@circuit.protected
async def send_message_with_protection(message):
    await message_bus.publish(message)
```

---

## 7. Performance Optimization

### 7.1 Message Batching

```python
# Batch messages for efficiency
messages = [message1, message2, message3]
await message_bus.publish_batch(messages)
```

### 7.2 Connection Pooling

```python
# Reuse connections
connection_pool = ConnectionPool(
    max_connections=10,
    idle_timeout=300
)

async with connection_pool.get_connection() as conn:
    await conn.send_message(message)
```

### 7.3 Message Compression

```python
# Compress large messages
await message_bus.publish(
    message=large_message,
    compress=True,
    compression_algorithm="gzip"
)
```

---

## 8. Security

### 8.1 Message Encryption

```python
# End-to-end encryption
await message_bus.publish(
    message=sensitive_message,
    encrypt=True,
    encryption_key=encryption_key
)
```

### 8.2 Message Authentication

```python
# Verify message sender
if not message_bus.verify_sender(message):
    raise SecurityError("Invalid message signature")
```

### 8.3 Access Control

```python
# Agent-based access control
await message_bus.set_permissions(
    agent_id="ceo_agent",
    can_publish=["task", "command"],
    can_subscribe=["query", "event"]
)
```

---

## 9. Monitoring and Observability

### 9.1 Metrics

```python
# Track messaging metrics
metrics.gauge("message_bus.queue_depth", queue_size)
metrics.increment("message_bus.messages_published")
metrics.timing("message_bus.delivery_latency", latency_ms)
```

### 9.2 Tracing

```python
# Distributed tracing
with tracer.start_span("publish_message") as span:
    span.set_attribute("message_type", message.message_type)
    span.set_attribute("recipient", message.recipient_id)
    await message_bus.publish(message)
```

---

## 10. Integration Examples

### 10.1 With Orchestration

```python
# Orchestrator sends tasks via message bus
await message_bus.publish(
    message_type=MessageType.TASK,
    recipient_id="ceo_agent",
    content={
        "workflow_id": "wf_001",
        "step": "analyze_strategy",
        "input": strategy_data
    }
)
```

### 10.2 With ML Pipeline

```python
# ML pipeline publishes training completion events
await message_bus.publish(
    message_type=MessageType.EVENT,
    content={
        "event": "model_trained",
        "model_id": "ceo_adapter_v1.2",
        "metrics": {"accuracy": 0.95}
    }
)
```

---

**Document Approval:**
- **Status:** Implemented and Active
- **Last Updated:** December 25, 2025
- **Next Review:** Quarterly
- **Owner:** AOS Communication Team
