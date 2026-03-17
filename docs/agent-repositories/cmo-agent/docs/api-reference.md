# API Reference — cmo-agent

## Module: `cmo_agent`

### Exports

| Symbol | Kind | Description |
|---|---|---|
| `CMOAgent` | Concrete class | Dual-purpose CMO agent |

---

## class `CMOAgent`

```python
class CMOAgent(LeadershipAgent)
```

Extends `LeadershipAgent` with dual-purpose marketing and leadership
capabilities.  Inherits all methods from `LeadershipAgent` and
`PurposeDrivenAgent`.

### Constructor

```python
CMOAgent(
    agent_id: str,
    name: Optional[str] = None,
    role: Optional[str] = None,
    marketing_purpose: Optional[str] = None,
    leadership_purpose: Optional[str] = None,
    purpose_scope: Optional[str] = None,
    success_criteria: Optional[List[str]] = None,
    tools: Optional[List[Any]] = None,
    system_message: Optional[str] = None,
    marketing_adapter_name: Optional[str] = None,
    leadership_adapter_name: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None,
)
```

#### Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `agent_id` | `str` | *required* | Unique identifier |
| `name` | `str` | `"CMO"` | Human-readable name |
| `role` | `str` | `"CMO"` | Role label |
| `marketing_purpose` | `str` | Standard CMO marketing purpose | Marketing purpose |
| `leadership_purpose` | `str` | Standard leadership purpose | Leadership purpose |
| `purpose_scope` | `str` | `"Marketing and Leadership domains"` | Scope |
| `success_criteria` | `List[str]` | `[]` | Success conditions |
| `tools` | `List[Any]` | `[]` | Tools via MCP |
| `system_message` | `str` | `""` | System message |
| `marketing_adapter_name` | `str` | `"marketing"` | Marketing LoRA adapter |
| `leadership_adapter_name` | `str` | `"leadership"` | Leadership LoRA adapter |
| `config` | `Dict[str, Any]` | `{}` | Configuration dict |

### Instance Attributes (additional to LeadershipAgent)

| Attribute | Type | Description |
|---|---|---|
| `marketing_purpose` | `str` | Marketing purpose string |
| `leadership_purpose` | `str` | Leadership purpose string |
| `marketing_adapter_name` | `str` | Marketing LoRA adapter name |
| `leadership_adapter_name` | `str` | Leadership LoRA adapter name |
| `purpose_adapter_mapping` | `Dict[str, str]` | Purpose → adapter mapping |

### Key inherited attribute

| Attribute | Default | Description |
|---|---|---|
| `adapter_name` | `marketing_adapter_name` | Currently active adapter (primary = marketing) |

---

### Methods

#### `get_agent_type() → List[str]`

Returns `["marketing", "leadership"]`.

---

#### `get_adapter_for_purpose(purpose_type: str) → str`

Return the LoRA adapter name for the specified purpose type.

**Parameters:**

| Name | Type | Description |
|---|---|---|
| `purpose_type` | `str` | `"marketing"` or `"leadership"` (case-insensitive) |

**Returns:** Adapter name string.

**Raises:** `ValueError` if `purpose_type` is not recognised.

---

#### `async execute_with_purpose(task, purpose_type="marketing") → Dict[str, Any]`

Execute a task using the LoRA adapter for the specified purpose.

**Parameters:**

| Name | Type | Default | Description |
|---|---|---|---|
| `task` | `Dict[str, Any]` | *required* | Task event dict |
| `purpose_type` | `str` | `"marketing"` | Purpose to use |

**Returns:** `handle_event()` result augmented with:

```python
{
    "status":       str,
    "processed_by": str,
    "purpose_type": str,   # "marketing" | "leadership"
    "adapter_used": str,   # adapter name that was active
    ...                    # other handle_event() fields
}
```

**Raises:** `ValueError` if `purpose_type` is not recognised.

**Guarantee:** `adapter_name` is always restored to its original value, even
if an exception is raised.

---

#### `async get_status() → Dict[str, Any]`

Return full CMO status including dual purpose-adapter information.

**Returns:**

```python
{
    # From get_purpose_status():
    "agent_id":                 str,
    "purpose":                  str,
    "purpose_scope":            str,
    "success_criteria":         List[str],
    "metrics":                  Dict[str, int],
    "active_goals":             int,
    "completed_goals":          int,
    "is_running":               bool,
    "total_events_processed":   int,

    # CMO additions:
    "agent_type":               "CMOAgent",
    "purposes": {
        "marketing": {
            "description": str,
            "adapter":     str,
        },
        "leadership": {
            "description": str,
            "adapter":     str,
        },
    },
    "purpose_adapter_mapping":  Dict[str, str],
    "primary_adapter":          str,
}
```

---

### Inherited from `LeadershipAgent`

- `make_decision(context, stakeholders, mode)`
- `_evaluate_decision(context)` — override for custom logic
- `consult_stakeholders(stakeholders, topic, context)` — requires message bus
- `get_decision_history(limit)`

### Inherited from `PurposeDrivenAgent`

- `initialize()`, `start()`, `stop()`
- `handle_event()`, `handle_message()`, `subscribe_to_event()`
- `evaluate_purpose_alignment()`, `make_purpose_driven_decision()`
- `add_goal()`, `update_goal_progress()`
- `get_purpose_status()`, `get_state()`, `health_check()`, `get_metadata()`
- `act()`, `execute_task()`
- `get_available_personas()`, `validate_personas()`
