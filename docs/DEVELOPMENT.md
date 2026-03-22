# AOS Development Guide

**Last Updated**: 2026-03-22  
**Audience**: AOS platform developers and contributors

---

## Repository Structure

This is a **meta-repository** that coordinates 15 focused sub-repositories via Git submodules. The meta-repo itself contains:

| File / Directory | Purpose |
|-----------------|---------|
| `function_app.py` | Azure Functions entry point for `aos-dispatcher` |
| `pyproject.toml` | Python package definition (`aos-dispatcher-azure` v4.0.0) |
| `host.json` | Azure Functions v4 host configuration |
| `README.md` | Architecture overview and repository map |
| `.gitmodules` | Submodule definitions (all 15 repos) |
| `docs/` | Cross-cutting documentation |
| `spec/` | Design specs and task tracking |
| `.github/` | CI/CD workflows, Copilot agent system |

---

## Working with Submodules

```bash
# After cloning, initialize all submodules
git submodule update --init --recursive

# Work on a specific submodule
cd aos-kernel
git checkout main
# make changes, commit, push within that repo

# Update the meta-repo pointer to the new commit
cd ..
git add aos-kernel
git commit -m "chore: update aos-kernel submodule reference"
```

Each submodule has its own tests, CI pipeline, and release cycle. Changes to a submodule must be committed and pushed in that repo before updating the meta-repo pointer.

---

## Cross-Repository Change Guidelines

When making changes that span multiple repositories:

1. **Start with the lowest-level dependency** (e.g., `purpose-driven-agent` → `leadership-agent` → `ceo-agent`)
2. **Update the interface contract** in the base package first, then update dependent packages
3. **Bump versions** in `pyproject.toml` following semver (patch for fixes, minor for features, major for breaking changes)
4. **Update dependency constraints** in downstream repos' `pyproject.toml` files
5. **Run CI** in each affected repo before updating submodule pointers in this meta-repo

---

## Agent Inheritance Chain

```
agent_framework.Agent (Microsoft)
    └── PurposeDrivenAgent          (purpose-driven-agent)
            └── LeadershipAgent     (leadership-agent)
                    └── CEOAgent    (ceo-agent)
                    └── CFOAgent    (cfo-agent)
                    └── CTOAgent    (cto-agent)
                    └── CSOAgent    (cso-agent)
                    └── CMOAgent    (cmo-agent)
```

When modifying the agent hierarchy:
- Changes to `PurposeDrivenAgent` API affect all downstream agents
- Changes to `LeadershipAgent` affect all C-suite agents
- Always add new capabilities to the lowest-level appropriate class

---

## Python Coding Conventions

- All packages use `pyproject.toml`; build system is either `hatchling` (e.g. `aos-intelligence`) or `setuptools` (e.g. `aos-dispatcher`, `aos-kernel`, `aos-client-sdk`)
- Package names: **kebab-case** (e.g., `aos-kernel`, `purpose-driven-agent`)
- Module names: **snake_case** (e.g., `aos_kernel`, `purpose_driven_agent`)
- Target **Python 3.11+**
- Follow **PEP 8** with 88-character line limit
- Use **type hints** on all function signatures
- Write **Google-style docstrings** for public functions and classes
- Use `from __future__ import annotations` at the top of each module

### Async Patterns

All workflow and SDK methods are `async`:

```python
@app.workflow("strategic-review")
async def strategic_review(request: WorkflowRequest) -> Dict[str, Any]:
    agents = await request.client.list_agents()
    return await request.client.start_orchestration(
        agent_ids=[a.agent_id for a in agents],
        purpose="Drive strategic review",
        context=request.body,
    )
```

Always `await` SDK calls — they are all coroutines.

---

## function_app.py Architecture

The `function_app.py` in this meta-repo is the **Azure Functions entry point** for `aos-dispatcher`. It follows a strict thin-wrapper pattern:

```python
import aos_dispatcher.dispatcher as dispatcher

app = func.FunctionApp()

def _make_response(result: tuple) -> func.HttpResponse:
    """Convert (body, status_code) tuple to HttpResponse."""
    ...

@app.function_name("submit_orchestration")
@app.route(route="orchestrations", methods=["POST"])
async def submit_orchestration(req: func.HttpRequest) -> func.HttpResponse:
    body, err = _require_json(req)
    if err:
        return err
    return _make_response(dispatcher.process_orchestration_request(body))
```

**Rules for `function_app.py`**:
1. Never import business logic directly — always delegate to `aos_dispatcher.dispatcher`
2. Always use `_make_response()` to convert library responses
3. Use `_require_json()` for any endpoint that expects a JSON body
4. Route names (function names) must match the endpoint documentation in [`API-REFERENCE.md`](API-REFERENCE.md)

---

## Testing

Each sub-repository has its own `tests/` directory with pytest.

```bash
# Run the full meta-repo CI validation
python3 -c "
import re, sys
with open('.gitmodules') as f:
    content = f.read()
paths = re.findall(r'^[\t ]*path = (.+)$', content, re.MULTILINE)
print(f'Registered submodules: {sorted(paths)}')
"

# For individual sub-repositories, run their own test suites
cd aos-kernel
pytest tests/ -v

cd aos-dispatcher
pytest tests/ -v
```

C-suite agent tests use `--rootdir` to avoid pytest namespace conflicts:

```bash
cd ceo-agent
pytest tests/ -v --rootdir=.
```

### Testing Client Apps with MockAOSClient

`aos-client-sdk` v7.0.0 provides `MockAOSClient` for local testing without a running AOS instance:

```python
from aos_client.testing import MockAOSClient

mock_client = MockAOSClient()
# configure mock responses, then inject into workflows
```

Full test suite across all repos: ~387 tests.

---

## Adding a New Endpoint to the Dispatcher

1. Add the handler function to `function_app.py`:

```python
@app.function_name("my_new_endpoint")
@app.route(route="my-resource/{id}", methods=["POST"])
async def my_new_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Description of the endpoint."""
    resource_id = req.route_params.get("id", "")
    body, err = _require_json(req)
    if err:
        return err
    return _make_response(dispatcher.my_operation(resource_id, body))
```

2. Implement `my_operation()` in `aos-dispatcher` (the library).

3. Update the module docstring at the top of `function_app.py` with the new endpoint.

4. Add the endpoint to [`API-REFERENCE.md`](API-REFERENCE.md).

---

## Adding a New C-Suite Agent

1. Create a new repository under the ASISaga organization: `https://github.com/ASISaga/<role>-agent`

2. Scaffold the repository following the pattern from `ceo-agent`:
   - `src/<role>_agent/agent.py` — agent class inheriting from `LeadershipAgent`
   - `pyproject.toml` — package definition
   - `azure.yaml` — azd deployment config with `host: ai.agent`
   - `.github/workflows/ci.yml` and `deploy.yml`
   - `tests/`

3. Add the submodule to this meta-repo:

```bash
git submodule add https://github.com/ASISaga/<role>-agent.git
git add .gitmodules <role>-agent
git commit -m "feat: add <role>-agent submodule"
```

4. Update the CI workflow to include the new submodule in the validation list.

5. Add the new repo to `README.md`, `.github/specs/repository.md`, and [`ARCHITECTURE.md`](ARCHITECTURE.md).

---

## Release Process

Each sub-repository follows its own release cycle. For meta-repo releases:

1. Ensure all submodule pointers are up-to-date
2. Update `pyproject.toml` version if the dispatcher entry point changed
3. Tag the meta-repo: `git tag v4.x.y && git push --tags`
4. Update `README.md` with any new architecture changes

---

## GitHub Copilot Agent System

This repository uses a structured Copilot agent meta-intelligence system in `.github/`:

- `.github/agents/` — Custom GitHub Copilot agents
- `.github/specs/` — Specifications used by agents
- `.github/prompts/` — Reusable Copilot prompts
- `.github/skills/` — Agent skill directories
- `.github/instructions/` — Path-activated coding standards

See `.github/docs/agent-system-overview.md` for a full description.

---

## References

- [ARCHITECTURE.md](ARCHITECTURE.md) — System architecture
- [API-REFERENCE.md](API-REFERENCE.md) — Dispatcher API
- [CONFIGURATION.md](CONFIGURATION.md) — Environment variables
- [DEPLOYMENT.md](DEPLOYMENT.md) — Deployment guide
