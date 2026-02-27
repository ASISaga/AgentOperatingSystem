# API Reference — purpose-driven-agent

## Module: `purpose_driven_agent`

### Exports

| Symbol | Kind | Description |
|---|---|---|
| `PurposeDrivenAgent` | Abstract class | Fundamental building block (ABC) |
| `GenericPurposeDrivenAgent` | Concrete class | General-purpose implementation |
| `ContextMCPServer` | Class | Lightweight MCP context server |
| `IMLService` | Abstract class | ML service interface |
| `NoOpMLService` | Concrete class | No-op ML service placeholder |

---

## class `PurposeDrivenAgent`

```python
class PurposeDrivenAgent(agent_framework.Agent, ABC)
```

**Abstract base class.** Cannot be instantiated directly.

### Constructor

```python
PurposeDrivenAgent(
    agent_id: str,
    purpose: str,
    name: Optional[str] = None,
    role: Optional[str] = None,
    agent_type: Optional[str] = None,
    purpose_scope: Optional[str] = None,
    tools: Optional[List[Any]] = None,
    system_message: Optional[str] = None,
    adapter_name: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None,
    aos: Optional[Any] = None,
    ml_service: Optional[IMLService] = None,
)
```

#### Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `agent_id` | `str` | *required* | Unique identifier |
| `purpose` | `str` | *required* | Long-term purpose (added to LLM context) |
| `name` | `str` | `agent_id` | Human-readable name |
| `role` | `str` | `"agent"` | Role label |
| `agent_type` | `str` | `"purpose_driven"` | Type label |
| `purpose_scope` | `str` | `"General purpose operation"` | Scope/boundaries |
| `tools` | `List[Any]` | `[]` | Tools available via MCP |
| `system_message` | `str` | `""` | System message override |
| `adapter_name` | `str` | `None` | LoRA adapter name |
| `config` | `Dict[str, Any]` | `{}` | Configuration dict (`"context_server"` sub-key) |
| `aos` | `Any` | `None` | AOS instance for persona queries |
| `ml_service` | `IMLService` | `NoOpMLService()` | ML backend implementation |

### Abstract Methods

#### `get_agent_type() → List[str]`

Return the list of personas/skills this agent uses.  Must be implemented by all concrete subclasses.

**Returns:** Non-empty list of persona name strings.

### Lifecycle Methods

#### `async initialize() → bool`

Set up MCP context server, load saved state, and store purpose in MCP.

**Returns:** `True` if successful.

#### `async start() → bool`

Start the perpetual operation loop.

**Returns:** `True` when the background task is scheduled.

#### `async stop() → bool`

Stop perpetual operations and persist state to MCP.

**Returns:** `True` if stopped cleanly.

### Messaging Methods

#### `async handle_event(event: Dict[str, Any]) → Dict[str, Any]`

Core event-processing method.  Evaluates purpose alignment, awakens the agent,
dispatches to registered handlers, saves MCP context, then sleeps.

**Parameters:**

| Name | Type | Description |
|---|---|---|
| `event` | `Dict[str, Any]` | Event dict; `"type"` and `"data"` keys used |

**Returns:** Response dict with `"status"`, `"processed_by"`, `"purpose_alignment"`, `"purpose"`.

#### `async handle_message(message: Dict[str, Any]) → Dict[str, Any]`

Alias for `handle_event`.

#### `async subscribe_to_event(event_type: str, handler: Callable) → bool`

Register an async handler for a named event type.

**Returns:** `True` on success.

### Purpose Methods

#### `async evaluate_purpose_alignment(action: Dict[str, Any]) → Dict[str, Any]`

Evaluate whether an action aligns with the agent's purpose.

**Returns:** Dict with `"aligned"` (bool), `"alignment_score"` (float 0–1), `"reasoning"` (str), `"timestamp"` (str).

#### `async make_purpose_driven_decision(decision_context: Dict[str, Any]) → Dict[str, Any]`

Select the best-aligned option from `decision_context["options"]`.

**Returns:** Decision dict with `"decision_id"`, `"selected_option"`, `"alignment_score"`.

#### `async add_goal(goal_description: str, success_criteria: List[str] = None, deadline: str = None) → str`

Add an active goal.  Returns the assigned goal ID.

#### `async update_goal_progress(goal_id: str, progress: float, notes: str = None) → bool`

Update goal progress (0.0–1.0).  Progress ≥ 1.0 marks the goal complete.

### Status Methods

#### `async get_purpose_status() → Dict[str, Any]`

Return a summary of purpose-driven operation.

**Returns:**

```python
{
    "agent_id": str,
    "purpose": str,
    "purpose_scope": str,
    "metrics": {
        "purpose_aligned_actions": int,
        "purpose_evaluations": int,
        "decisions_made": int,
        "goals_achieved": int,
    },
    "active_goals": int,
    "completed_goals": int,
    "is_running": bool,
    "total_events_processed": int,
}
```

#### `async get_state() → Dict[str, Any]`

Return runtime state.

**Returns:**

```python
{
    "agent_id": str,
    "adapter_name": Optional[str],
    "is_running": bool,
    "sleep_mode": bool,
    "wake_count": int,
    "total_events_processed": int,
    "subscriptions": List[str],
    "mcp_context_preserved": bool,
}
```

#### `async health_check() → Dict[str, Any]`

Lightweight health check.  Returns `{"agent_id", "state", "healthy", "timestamp"}`.

#### `get_metadata() → Dict[str, Any]`

Return static agent metadata.

### ML / Action Methods

#### `async act(action: str, params: Dict[str, Any]) → Any`

Execute a named action.  Supported `action` values:

| Action | Description |
|---|---|
| `"trigger_lora_training"` | Trigger LoRA training via `IMLService` |
| `"run_azure_ml_pipeline"` | Run Azure ML pipeline |
| `"aml_infer"` | Run inference |

#### `async execute_task(task: Dict[str, Any]) → Dict[str, Any]`

Execute a task dict with `"action"` and `"params"` keys.

### AOS Integration

#### `get_available_personas() → List[str]`

Query AOS for available LoRA adapter personas.  Falls back to a built-in list.

#### `validate_personas(personas: List[str]) → bool`

Check that all requested personas are registered in AOS.

---

## class `GenericPurposeDrivenAgent`

```python
class GenericPurposeDrivenAgent(PurposeDrivenAgent)
```

Concrete general-purpose implementation.  Inherits all `PurposeDrivenAgent`
methods.  Constructor signature is identical to `PurposeDrivenAgent`.

### `get_agent_type() → List[str]`

Returns `["generic"]`.

---

## class `ContextMCPServer`

```python
class ContextMCPServer(agent_id: str, config: Optional[Dict[str, Any]] = None)
```

Lightweight in-process MCP context store.

### Methods

| Method | Returns | Description |
|---|---|---|
| `async initialize()` | `bool` | Initialise the server |
| `async set_context(key, value)` | `bool` | Store a value |
| `async get_context(key)` | `Optional[Any]` | Retrieve a value |
| `async get_all_context()` | `Dict[str, Any]` | Return entire context dict |
| `async delete_context(key)` | `bool` | Remove an entry |
| `async clear_context()` | `bool` | Remove all entries |
| `async add_event(event)` | `bool` | Append to event history |
| `async get_recent_events(limit)` | `List[Dict]` | Retrieve recent events |
| `async add_memory(item)` | `bool` | Add semantic memory item |
| `async get_memory(limit)` | `List[Dict]` | Retrieve memory items |
| `async get_stats()` | `Dict[str, Any]` | Return usage statistics |

---

## class `IMLService`

```python
class IMLService(ABC)
```

Abstract interface for ML pipeline operations.

### Abstract Methods

#### `async trigger_lora_training(training_params: Dict, adapters: List[Dict]) → str`
#### `async run_pipeline(subscription_id: str, resource_group: str, workspace_name: str) → str`
#### `async infer(agent_id: str, prompt: str) → Dict[str, Any]`

---

## class `NoOpMLService`

Implements `IMLService`.  Every method raises `NotImplementedError`.

---

## Instance Attributes

### `PurposeDrivenAgent` public attributes

| Attribute | Type | Description |
|---|---|---|
| `agent_id` | `str` | Unique agent identifier |
| `name` | `str` | Human-readable name |
| `role` | `str` | Role label |
| `agent_type` | `str` | Type label |
| `purpose` | `str` | Long-term purpose |
| `purpose_scope` | `str` | Purpose scope |
| `adapter_name` | `Optional[str]` | LoRA adapter name |
| `is_running` | `bool` | Whether perpetual loop is active |
| `sleep_mode` | `bool` | Whether agent is currently sleeping |
| `wake_count` | `int` | Total awaken cycles |
| `total_events_processed` | `int` | Cumulative event count |
| `active_goals` | `List[Dict]` | Currently active goals |
| `completed_goals` | `List[Dict]` | Completed goals |
| `purpose_metrics` | `Dict[str, int]` | Purpose-alignment counters |
| `mcp_context_server` | `Optional[ContextMCPServer]` | MCP instance (set after `initialize()`) |
| `config` | `Dict[str, Any]` | Configuration dict |
| `state` | `str` | Current state string (`"initialized"`, `"running"`) |
| `logger` | `logging.Logger` | Bound logger |
