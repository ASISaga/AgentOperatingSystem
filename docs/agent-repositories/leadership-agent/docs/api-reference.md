# API Reference — leadership-agent

## Module: `leadership_agent`

### Exports

| Symbol | Kind | Description |
|---|---|---|
| `LeadershipAgent` | Concrete class | Leadership and decision-making agent |

---

## class `LeadershipAgent`

```python
class LeadershipAgent(PurposeDrivenAgent)
```

Extends `PurposeDrivenAgent` with leadership capabilities.  Inherits all
methods from `PurposeDrivenAgent` (see the `purpose-driven-agent` API
reference for the full inherited API).

### Constructor

```python
LeadershipAgent(
    agent_id: str,
    name: Optional[str] = None,
    role: Optional[str] = None,
    purpose: Optional[str] = None,
    purpose_scope: Optional[str] = None,
    tools: Optional[List[Any]] = None,
    system_message: Optional[str] = None,
    adapter_name: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None,
    **kwargs,
)
```

#### Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `agent_id` | `str` | *required* | Unique identifier |
| `name` | `str` | `agent_id` | Human-readable name |
| `role` | `str` | `"leader"` | Role label |
| `purpose` | `str` | Standard leadership purpose | Long-term purpose |
| `purpose_scope` | `str` | `"Leadership and decision-making domain"` | Scope |
| `tools` | `List[Any]` | `[]` | Tools via MCP |
| `system_message` | `str` | `""` | System message |
| `adapter_name` | `str` | `"leadership"` | LoRA adapter name |
| `config` | `Dict[str, Any]` | `{}` | Configuration dict |
| `**kwargs` | | | Forwarded to `PurposeDrivenAgent` |

### Instance Attributes (additional to PurposeDrivenAgent)

| Attribute | Type | Description |
|---|---|---|
| `decisions_made` | `List[Dict[str, Any]]` | All decisions made, newest last |
| `stakeholders` | `List[str]` | Registered stakeholder agent IDs |

---

### Methods

#### `get_agent_type() → List[str]`

Returns `["leadership"]`.

---

#### `async make_decision(context, stakeholders=None, mode="autonomous") → Dict[str, Any]`

Make and record a decision.

**Parameters:**

| Name | Type | Default | Description |
|---|---|---|---|
| `context` | `Dict[str, Any]` | *required* | Decision context |
| `stakeholders` | `List[str]` | `[]` | Stakeholder agent IDs |
| `mode` | `str` | `"autonomous"` | Decision mode |

**Returns:**

```python
{
    "id":           str,            # UUID
    "agent_id":     str,
    "context":      Dict[str, Any],
    "mode":         str,            # "autonomous" | "consensus" | "delegated"
    "stakeholders": List[str],
    "timestamp":    str,            # ISO-8601
    "decision":     Any,            # from _evaluate_decision()
    "confidence":   float,          # 0.0–1.0
    "rationale":    str,
}
```

---

#### `async _evaluate_decision(context) → Any`

Internal — evaluate the decision context.  Override in subclasses to provide
domain-specific decision logic.

**Default implementation:** returns `{"decision": "pending", "reason": "not_implemented"}`.

---

#### `async consult_stakeholders(stakeholders, topic, context) → List[Dict[str, Any]]`

Consult stakeholder agents on a topic.

**Parameters:**

| Name | Type | Description |
|---|---|---|
| `stakeholders` | `List[str]` | Agent IDs to consult |
| `topic` | `str` | Consultation topic |
| `context` | `Dict[str, Any]` | Contextual information |

**Raises:** `NotImplementedError` — override and integrate a message bus.

---

#### `async get_decision_history(limit=10) → List[Dict[str, Any]]`

Return recent decisions.

**Parameters:**

| Name | Type | Default | Description |
|---|---|---|---|
| `limit` | `int` | `10` | Max decisions to return |

**Returns:** List of decision dicts (newest last).

---

### Inherited from `PurposeDrivenAgent`

All lifecycle, messaging, purpose, status, and ML methods are inherited.
See the `purpose-driven-agent` API reference for full documentation:

- `initialize()`, `start()`, `stop()`
- `handle_event()`, `handle_message()`, `subscribe_to_event()`
- `evaluate_purpose_alignment()`, `make_purpose_driven_decision()`
- `add_goal()`, `update_goal_progress()`
- `get_purpose_status()`, `get_state()`, `health_check()`, `get_metadata()`
- `act()`, `execute_task()`
- `get_available_personas()`, `validate_personas()`
