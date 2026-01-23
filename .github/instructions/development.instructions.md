# Development Workflow and Best Practices

## Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[full]"  # Install with all optional dependencies
```

## Testing

### Running Tests

```bash
# All tests
pytest tests/

# Run specific test file
pytest tests/test_perpetual_agents.py

# Run with verbose output
pytest -v tests/

# Run async tests (most tests use async/await)
pytest tests/ -v --asyncio-mode=auto

# With coverage (if pytest-cov is installed)
pytest tests/ --cov=src/AgentOperatingSystem
```

### Test Organization

- `tests/test_*.py` - Unit and integration tests
- Tests use pytest and pytest-asyncio
- Most tests are async due to the async nature of AOS

### Writing Tests

- Use `pytest.mark.asyncio` for async tests
- Follow existing test patterns in the tests/ directory
- Mock Azure services when appropriate
- Test both success and failure cases

## Code Quality

- Follow PEP 8 style guidelines
- Use type hints where possible
- Write async functions for I/O operations
- Use meaningful variable names

## Common Commands

```bash
# Run a specific test
pytest tests/test_integration.py -v

# Check Python syntax
python -m py_compile src/AgentOperatingSystem/agents/*.py

# List all test files
find tests/ -name "test_*.py"
```

## Common Gotchas & Best Practices

### Async/Await

- **Always** use `await` for async functions
- Use `asyncio.run()` for running async code from sync context
- Be careful with event loops in tests
- Most AOS code is asynchronous:

```python
async def example():
    await agent.initialize()
    result = await agent.process_event(event)
    await agent.cleanup()
```

### Azure Services

- Many features require Azure credentials (set in environment or local.settings.json)
- Some tests may be skipped if Azure services are not available
- Use mock services for local testing when possible

### Dependencies

- Install with `[full]` option for all features: `pip install -e ".[full]"`
- Optional dependency groups: `azure`, `ml`, `mcp`
- Some tests may require specific dependencies

### State Management

- Agents maintain state via ContextMCPServer
- State persists across events (perpetual nature)
- Clean up state in tests to avoid cross-test contamination

### Error Handling

- Use try/except blocks for Azure service calls
- Implement retry logic with exponential backoff
- Log errors with structured logging

## Learning Path

### For First-Time Contributors

1. Read `README.md` - Understand the core concept of perpetual vs task-based
2. Read `docs/architecture/ARCHITECTURE.md` - Understand the layered architecture
3. Review `examples/perpetual_agents_example.py` - See usage examples
4. Run simple tests: `pytest tests/simple_test.py -v`
5. Read `docs/development/CONTRIBUTING.md` - Understand contribution guidelines

### For Code Changes

1. Identify the relevant module (agents/, orchestration/, messaging/, etc.)
2. Review existing code in that module
3. Check for related tests in tests/
4. Make minimal changes
5. Run tests: `pytest tests/test_<module>.py`
6. Update documentation if needed

### For Bug Fixes

1. Write a failing test that reproduces the bug
2. Fix the code
3. Verify the test passes
4. Run full test suite to ensure no regressions

## Finding Your Way Around

### To understand agents:

- `src/AgentOperatingSystem/agents/` - Agent implementations
- `examples/perpetual_agents_example.py` - Usage examples
- `tests/test_perpetual_agents.py` - Agent tests

### To understand orchestration:

- `src/AgentOperatingSystem/orchestration/` - Orchestration engine
- `docs/architecture/ARCHITECTURE.md` - Orchestration architecture
- `tests/test_integration.py` - Orchestration tests

### To understand Azure integration:

- `function_app.py` - Azure Functions setup
- `azure_functions/` - Azure-specific code
- `tests/test_azure_functions_infrastructure.py` - Azure tests

### To understand messaging:

- `src/AgentOperatingSystem/messaging/` - Message bus implementation
- `docs/a2a_communication.md` - Agent-to-agent communication
- Inter-agent communication patterns

## Tips for Efficient Work

1. **Use grep/search**: This is a large codebase. Use grep to find relevant code:
   ```bash
   grep -r "PurposeDrivenAgent" src/
   find src/ -name "*orchestr*.py"
   ```

2. **Check examples first**: Before implementing something, check if there's an example in `examples/`

3. **Read tests**: Tests are often the best documentation for how to use a feature

4. **Start small**: Make minimal changes to achieve your goal

5. **Async is key**: Remember that almost everything is async. Use `await` liberally

6. **Azure context**: Many features are Azure-specific. Understand the Azure service being used

7. **State is persistent**: Remember that agents are perpetual and maintain state

## FAQ

**Q: How do I run tests?**
A: `pytest tests/` - Most tests are async and use pytest-asyncio

**Q: What Python version is required?**
A: Python 3.8 or higher (see pyproject.toml)

**Q: How do I install dependencies?**
A: `pip install -e ".[full]"` for all features, or `pip install -e .` for core only

**Q: Why are agents "perpetual"?**
A: Unlike traditional frameworks where agents run for a task then stop, AOS agents register once and run indefinitely, responding to events. This is the core architectural difference.

**Q: What is PurposeDrivenAgent?**
A: It's the fundamental building block of AOS, combining perpetual operation with purpose alignment and using ContextMCPServer for state preservation.

**Q: How do I test Azure Functions locally?**
A: Use the Azure Functions Core Tools, but many tests use mocks for local testing

**Q: What if tests fail due to missing Azure credentials?**
A: Many tests will skip or mock Azure services if credentials are not available. For full testing, configure Azure credentials in local.settings.json

## Remember

This is an operating system for AI agents, not a traditional application. Think in terms of persistent processes, event-driven architecture, and long-running state, not request-response or task-based execution.
