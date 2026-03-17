# Requirements: Merge Parent Directories into Submodules

## Context

The `agent-operating-system` repository contains both:
1. **Parent directories** (`src/`, `deployment/`, `config/`, `data/`, `docs/`, `tests/`) — legacy monolithic code from before the submodule split
2. **Submodules** (`aos-kernel/`, `aos-intelligence/`, `aos-infrastructure/`, `aos-dispatcher/`, `aos-client-sdk/`) — the target modular architecture

The parent directories contain implementation code that duplicates or extends what's in the submodules. This code must be merged into the appropriate submodules, and the parent directories removed.

## Requirements (EARS Notation)

### R1 — Source Code Merge (src/ → kernel + intelligence)
WHEN the refactoring is complete, THE SYSTEM SHALL have all source code from `src/AgentOperatingSystem/` merged into the appropriate submodule:
- Kernel modules (agents, apps, auth, config, environment, executor, extensibility, governance, mcp, messaging, monitoring, observability, orchestration, platform, reliability, services, shared, storage, testing) → `aos-kernel/src/AgentOperatingSystem/`
- Intelligence modules (knowledge, learning, ml) → `aos-intelligence/src/aos_intelligence/`
- Top-level files (`__init__.py`, `agent_operating_system.py`) → `aos-kernel/src/AgentOperatingSystem/`

### R2 — Deployment Merge (deployment/ → aos-infrastructure)
WHEN the refactoring is complete, THE SYSTEM SHALL have all unique files from `deployment/` merged into `aos-infrastructure/deployment/`, preserving any files that exist only in the parent.

### R3 — Config Distribution
WHEN the refactoring is complete, THE SYSTEM SHALL have config files distributed:
- `consolidated_config.json` → `aos-kernel/config/`
- `self_learning_config.json` → `aos-intelligence/config/`
- `example_app_registry.json` → `aos-client-sdk/config/`

### R4 — Data Distribution (data/ → intelligence)
WHEN the refactoring is complete, THE SYSTEM SHALL have all knowledge/learning JSON data files in `aos-intelligence/data/`.

### R5 — Documentation Distribution
WHEN the refactoring is complete, THE SYSTEM SHALL have all documentation from `docs/` distributed to the appropriate submodule based on topic domain.

### R6 — Test Distribution
WHEN the refactoring is complete, THE SYSTEM SHALL have all test files from `tests/` distributed to the appropriate submodule based on what they test.

### R7 — Parent Cleanup
WHEN all merges are validated, THE SYSTEM SHALL remove the now-empty parent directories (`src/`, `deployment/`, `config/`, `data/`, `docs/`, `tests/`).

### R8 — Submodule Integrity
THE SYSTEM SHALL preserve all existing files in submodules (never overwrite newer submodule code with older parent code). When conflicts exist between parent-only files and submodule-only files, both are preserved.

### R9 — Git History
WHEN files are moved, THE SYSTEM SHALL use git operations that preserve traceability.

## Confidence Score: 90%
**Rationale**: Clear file mapping, well-understood submodule boundaries, straightforward file operations. Proceeding with full implementation.
