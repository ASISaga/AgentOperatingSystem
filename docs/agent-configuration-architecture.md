# Agent YAML Configuration Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Agent Configuration                         │
│                        (agent.yaml)                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  agent_id: cmo                                                  │
│  agent_type: cmo                                                │
│                                                                 │
│  purposes:                                                      │
│    - name: marketing                                            │
│      adapter_name: marketing  ←──┐                             │
│    - name: leadership             │                             │
│      adapter_name: leadership ←──┼──┐                          │
│                                   │  │                          │
│  mcp_tools:                       │  │                          │
│    - server_name: analytics       │  │                          │
│      tool_name: get_metrics       │  │                          │
│                                   │  │                          │
│  capabilities:                    │  │                          │
│    - Marketing strategy           │  │                          │
│    - Team leadership              │  │                          │
└───────────────────────────────────┼──┼──────────────────────────┘
                                    │  │
                    ┌───────────────┘  └─────────────┐
                    │                                  │
                    ▼                                  ▼
        ┌───────────────────────┐        ┌───────────────────────┐
        │  Marketing LoRA       │        │  Leadership LoRA      │
        │     Adapter           │        │      Adapter          │
        ├───────────────────────┤        ├───────────────────────┤
        │ Domain Knowledge:     │        │ Domain Knowledge:     │
        │ - Marketing language  │        │ - Leadership language │
        │ - Marketing concepts  │        │ - Decision patterns   │
        │ - Brand vocabulary    │        │ - Coordination skills │
        │ - CMO persona         │        │ - Strategic thinking  │
        └───────────┬───────────┘        └──────────┬────────────┘
                    │                               │
                    └───────────┬───────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   CMOAgent Instance   │
                    ├───────────────────────┤
                    │ Purpose-to-Adapter:   │
                    │   marketing → M-LoRA  │
                    │   leadership → L-LoRA │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │  Primary LLM Context  │
                    ├───────────────────────┤
                    │ Purposes injected:    │
                    │ - Marketing purpose   │
                    │ - Leadership purpose  │
                    │                       │
                    │ MCP Context Server:   │
                    │ - State preservation  │
                    │ - Tools access        │
                    │ - Domain capabilities │
                    └───────────────────────┘
```

## Purpose-to-Adapter Flow

```
┌──────────────┐
│  YAML File   │
│              │
│ purposes:    │
│   - name: X  │───┐
│     adapter: │   │
│       "foo"  │   │
└──────────────┘   │
                   │
                   │  from_yaml()
                   │  reads YAML
                   ▼
        ┌──────────────────┐
        │ PurposeDrivenAgent│
        │   Constructor     │
        ├──────────────────┤
        │ 1. Parse YAML    │
        │ 2. Extract:      │
        │    - purposes[]  │
        │    - adapter map │
        │    - mcp_tools[] │
        │    - capabilities│
        └─────────┬────────┘
                  │
                  │  initialize()
                  ▼
        ┌──────────────────┐
        │  MCP Context      │
        │     Server        │
        ├──────────────────┤
        │ set_context():   │
        │ - purpose        │
        │ - purposes[]     │
        │ - mcp_tools[]    │
        │ - capabilities   │
        └─────────┬────────┘
                  │
                  │  Stored in
                  │  LLM context
                  ▼
        ┌──────────────────┐
        │  Agent Runtime   │
        │                  │
        │ Uses:            │
        │ - LoRA adapter   │
        │ - Purpose guide  │
        │ - MCP tools      │
        └──────────────────┘
```

## Multi-Purpose Agent Execution

```
           CMOAgent.execute_with_purpose(task, "marketing")
                              │
                              ▼
                ┌─────────────────────────┐
                │ get_adapter_for_purpose │
                │      ("marketing")      │
                └────────────┬────────────┘
                             │
                             ▼
                  Returns: "marketing"
                             │
                             ▼
                ┌─────────────────────────┐
                │  Switch to Marketing    │
                │     LoRA Adapter        │
                └────────────┬────────────┘
                             │
                             ▼
                ┌─────────────────────────┐
                │  Execute Task with:     │
                │  - Marketing knowledge  │
                │  - Marketing persona    │
                │  - Marketing purpose    │
                └────────────┬────────────┘
                             │
                             ▼
                ┌─────────────────────────┐
                │  Restore Original       │
                │     Adapter             │
                └─────────────────────────┘


           CMOAgent.execute_with_purpose(task, "leadership")
                              │
                              ▼
                ┌─────────────────────────┐
                │ get_adapter_for_purpose │
                │     ("leadership")      │
                └────────────┬────────────┘
                             │
                             ▼
                  Returns: "leadership"
                             │
                             ▼
                ┌─────────────────────────┐
                │  Switch to Leadership   │
                │     LoRA Adapter        │
                └────────────┬────────────┘
                             │
                             ▼
                ┌─────────────────────────┐
                │  Execute Task with:     │
                │  - Leadership knowledge │
                │  - Leadership persona   │
                │  - Leadership purpose   │
                └────────────┬────────────┘
                             │
                             ▼
                ┌─────────────────────────┐
                │  Restore Original       │
                │     Adapter             │
                └─────────────────────────┘
```

## Data Flow

```
Step 1: Configuration File
──────────────────────────
config/agents/cmo_agent.yaml
  ↓
  Contains: purposes, adapters, mcp_tools, capabilities


Step 2: Loading
───────────────
CMOAgent.from_yaml("config/agents/cmo_agent.yaml")
  ↓
  Parses YAML → Creates agent instance with configuration


Step 3: Initialization
──────────────────────
await agent.initialize()
  ↓
  Stores configuration in MCP Context Server
  Purpose → LLM Context
  Adapters → Purpose mapping


Step 4: Runtime Execution
─────────────────────────
await agent.execute_with_purpose(task, "marketing")
  ↓
  Switches to "marketing" LoRA adapter
  Uses marketing purpose from context
  Executes task with marketing domain knowledge


Step 5: State Persistence
─────────────────────────
MCP Context Server maintains:
  - Agent state across events
  - Purpose alignment tracking
  - Decision history
  - Goal progress
```

## Key Architectural Concepts

### 1. Declarative Configuration
```
YAML (What) → Code reads and applies (How)
```

### 2. Purpose-to-Adapter Mapping
```
Purpose Description → Guides behavior (LLM context)
Adapter Name → Provides expertise (LoRA knowledge)
```

### 3. Multi-Purpose Support
```
Single Agent → Multiple Purposes → Multiple Adapters
            → Switch based on task type
```

### 4. MCP Integration
```
MCP Context Server:
  ├─ State Preservation
  ├─ Purpose Storage
  ├─ Tool Access
  └─ Domain Capabilities
```

### 5. Backward Compatibility
```
YAML-based:   Agent.from_yaml("config.yaml")
Code-based:   Agent(agent_id, purpose, adapter_name)
              ↓
           Both supported ✅
```
