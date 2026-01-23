# Async Python Testing for AOS

## Description
Expert knowledge for testing asynchronous Python code in the Agent Operating System. AOS is heavily async-based, and proper async testing patterns are critical for reliable tests.

## When to Use This Skill
- Writing tests for async functions
- Testing async generators and iterators
- Mocking async calls and services
- Debugging async test failures
- Understanding pytest-asyncio patterns
- Testing concurrent operations

## Key Concepts

### Why Async in AOS?
AOS uses async/await extensively because:
- Azure SDK is async-based
- I/O operations (network, storage) benefit from async
- Agent orchestration requires concurrent operations
- Better resource utilization for perpetual agents

### Async vs Sync Testing
```python
# Sync test (traditional)
def test_something():
    result = function()
    assert result == expected

# Async test (AOS)
@pytest.mark.asyncio
async def test_something_async():
    result = await async_function()
    assert result == expected
```

## Testing Patterns

### Basic Async Test
```python
import pytest

@pytest.mark.asyncio
async def test_basic_async():
    """Simple async test."""
    async def fetch_data():
        return "data"
    
    result = await fetch_data()
    assert result == "data"
```

### Testing Async Functions with Setup/Teardown
```python
import pytest

@pytest.mark.asyncio
async def test_with_setup_teardown():
    """Test with async setup and teardown."""
    # Setup
    agent = MyAgent()
    await agent.initialize()
    
    try:
        # Test
        result = await agent.process()
        assert result is not None
        
    finally:
        # Teardown
        await agent.cleanup()
```

### Using Fixtures
```python
import pytest

@pytest.fixture
async def initialized_agent():
    """Async fixture for agent."""
    agent = MyAgent()
    await agent.initialize()
    yield agent
    await agent.cleanup()

@pytest.mark.asyncio
async def test_with_fixture(initialized_agent):
    """Test using async fixture."""
    result = await initialized_agent.process()
    assert result is not None
```

### Testing Multiple Async Operations
```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_concurrent_operations():
    """Test multiple concurrent async operations."""
    async def operation_1():
        await asyncio.sleep(0.1)
        return "op1"
    
    async def operation_2():
        await asyncio.sleep(0.1)
        return "op2"
    
    # Run concurrently
    results = await asyncio.gather(
        operation_1(),
        operation_2()
    )
    
    assert results == ["op1", "op2"]
```

## Mocking Async Code

### Mocking Async Functions
```python
import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_with_async_mock():
    """Test with AsyncMock."""
    # Create mock
    mock_service = AsyncMock()
    mock_service.fetch_data.return_value = {"data": "test"}
    
    # Use mock
    result = await mock_service.fetch_data()
    assert result == {"data": "test"}
    
    # Verify call
    mock_service.fetch_data.assert_called_once()
```

### Mocking Azure Services
```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_with_mocked_azure():
    """Test with mocked Azure services."""
    with patch('azure.storage.blob.BlobServiceClient') as mock_blob:
        # Configure mock
        mock_client = AsyncMock()
        mock_blob.from_connection_string.return_value = mock_client
        mock_client.get_blob_client.return_value.download_blob.return_value = b"data"
        
        # Test code that uses Azure Blob
        from AgentOperatingSystem.storage import AzureBlobStorage
        storage = AzureBlobStorage("connection_string")
        data = await storage.download("container", "blob")
        
        assert data == b"data"
```

### Mocking Async Context Managers
```python
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_async_context_manager():
    """Test async context manager."""
    mock_resource = AsyncMock()
    mock_resource.__aenter__.return_value = mock_resource
    mock_resource.__aexit__.return_value = None
    mock_resource.do_something.return_value = "result"
    
    async with mock_resource as resource:
        result = await resource.do_something()
        assert result == "result"
    
    mock_resource.__aenter__.assert_called_once()
    mock_resource.__aexit__.assert_called_once()
```

## Testing AOS Components

### Testing Perpetual Agents
```python
import pytest
from AgentOperatingSystem.agents import GenericPurposeDrivenAgent

@pytest.mark.asyncio
async def test_perpetual_agent():
    """Test perpetual agent lifecycle."""
    agent = GenericPurposeDrivenAgent(
        agent_id="test",
        purpose="Testing",
        adapter_name="test"
    )
    
    # Initialize
    await agent.initialize()
    assert agent.context_server is not None
    
    # Test operation
    event = {"type": "test_event"}
    result = await agent.handle_event(event)
    
    # Cleanup
    await agent.cleanup()
```

### Testing Agent Orchestration
```python
import pytest
from AgentOperatingSystem.orchestration import AgentOrchestrator

@pytest.mark.asyncio
async def test_orchestration():
    """Test agent orchestration."""
    orchestrator = AgentOrchestrator()
    await orchestrator.initialize()
    
    try:
        # Register agents
        agent1 = create_test_agent("agent1")
        agent2 = create_test_agent("agent2")
        
        await orchestrator.register_agent(agent1)
        await orchestrator.register_agent(agent2)
        
        # Test orchestration
        result = await orchestrator.coordinate_agents(
            task="test_task"
        )
        
        assert result is not None
        
    finally:
        await orchestrator.cleanup()
```

### Testing Message Bus
```python
import pytest
from AgentOperatingSystem.messaging import MessageBus

@pytest.mark.asyncio
async def test_message_bus():
    """Test async message bus."""
    bus = MessageBus()
    await bus.initialize()
    
    received_messages = []
    
    async def message_handler(message):
        received_messages.append(message)
    
    # Subscribe
    await bus.subscribe("test_topic", message_handler)
    
    # Publish
    await bus.publish("test_topic", {"data": "test"})
    
    # Wait for processing
    await asyncio.sleep(0.1)
    
    # Verify
    assert len(received_messages) == 1
    assert received_messages[0]["data"] == "test"
    
    await bus.cleanup()
```

## Common Patterns

### Testing Timeouts
```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_with_timeout():
    """Test operation with timeout."""
    async def slow_operation():
        await asyncio.sleep(10)
        return "done"
    
    # Test that operation times out
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(slow_operation(), timeout=0.1)
```

### Testing Retries
```python
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_retry_logic():
    """Test retry mechanism."""
    mock_service = AsyncMock()
    
    # Fail twice, then succeed
    mock_service.call.side_effect = [
        Exception("Error 1"),
        Exception("Error 2"),
        "success"
    ]
    
    # Function with retry logic
    async def call_with_retry(max_retries=3):
        for attempt in range(max_retries):
            try:
                return await mock_service.call()
            except Exception:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(0.1)
    
    result = await call_with_retry()
    assert result == "success"
    assert mock_service.call.call_count == 3
```

### Testing Async Generators
```python
import pytest

@pytest.mark.asyncio
async def test_async_generator():
    """Test async generator."""
    async def async_range(n):
        for i in range(n):
            await asyncio.sleep(0.01)
            yield i
    
    results = []
    async for value in async_range(3):
        results.append(value)
    
    assert results == [0, 1, 2]
```

### Testing Error Handling
```python
import pytest

@pytest.mark.asyncio
async def test_error_handling():
    """Test async error handling."""
    async def failing_function():
        raise ValueError("Test error")
    
    # Test that error is raised
    with pytest.raises(ValueError, match="Test error"):
        await failing_function()
```

## Pytest Configuration

### pytest.ini or pyproject.toml
```ini
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    asyncio: async tests
    integration: integration tests
    unit: unit tests
```

### Running Async Tests
```bash
# Run all async tests
pytest tests/ -v

# Run with asyncio mode auto
pytest tests/ --asyncio-mode=auto

# Run specific async test
pytest tests/test_perpetual_agents.py::test_agent_initialization -v

# Run with markers
pytest -m asyncio tests/

# Show async warnings
pytest tests/ -v -W default
```

## Common Issues and Solutions

### Issue: "RuntimeError: Event loop is closed"
**Problem**: Event loop closed prematurely.

**Solution**:
```python
# Use pytest-asyncio which manages event loop
@pytest.mark.asyncio
async def test_function():
    # pytest-asyncio handles event loop
    result = await async_operation()
    assert result
```

### Issue: "coroutine was never awaited"
**Problem**: Forgot to await async function.

**Solution**:
```python
# Wrong
result = async_function()  # Returns coroutine, not result

# Correct
result = await async_function()
```

### Issue: Tests Hang Indefinitely
**Problem**: Awaiting something that never completes.

**Solution**:
```python
# Add timeout
@pytest.mark.asyncio
async def test_with_timeout():
    async with asyncio.timeout(5):  # Python 3.11+
        result = await potentially_hanging_operation()
    
    # Or for older Python
    result = await asyncio.wait_for(
        potentially_hanging_operation(),
        timeout=5.0
    )
```

### Issue: "Task was destroyed but it is pending"
**Problem**: Tasks not properly cleaned up.

**Solution**:
```python
@pytest.mark.asyncio
async def test_cleanup():
    task = asyncio.create_task(background_operation())
    
    try:
        # Test code
        await something()
    finally:
        # Cleanup
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
```

### Issue: Mocks Not Working with Async
**Problem**: Using MagicMock instead of AsyncMock.

**Solution**:
```python
# Wrong
mock = MagicMock()
await mock.async_method()  # Will fail

# Correct
mock = AsyncMock()
await mock.async_method()  # Works correctly
```

## Best Practices

1. **Always use @pytest.mark.asyncio**: Mark all async tests
2. **Use AsyncMock for async mocks**: Not regular MagicMock
3. **Clean up resources**: Use try/finally or fixtures
4. **Test both success and failure**: Cover error paths
5. **Use timeouts**: Prevent hanging tests
6. **Avoid blocking calls**: Use async alternatives
7. **Test concurrent scenarios**: Use asyncio.gather
8. **Mock external services**: Don't rely on real Azure/network
9. **Use fixtures for setup**: Reuse common setup code
10. **Test cancellation**: Verify cleanup on task cancellation

## Example Test File

```python
"""
Test module for async agent operations.
"""
import pytest
import asyncio
from unittest.mock import AsyncMock
from AgentOperatingSystem.agents import GenericPurposeDrivenAgent


@pytest.fixture
async def test_agent():
    """Create test agent."""
    agent = GenericPurposeDrivenAgent(
        agent_id="test",
        purpose="Testing",
        adapter_name="test"
    )
    await agent.initialize()
    yield agent
    await agent.cleanup()


@pytest.mark.asyncio
async def test_agent_initialization(test_agent):
    """Test agent initializes correctly."""
    assert test_agent is not None
    assert test_agent.agent_id == "test"
    assert test_agent.context_server is not None


@pytest.mark.asyncio
async def test_agent_event_processing(test_agent):
    """Test agent processes events."""
    event = {"type": "test", "data": "test"}
    result = await test_agent.handle_event(event)
    assert result is not None


@pytest.mark.asyncio
async def test_concurrent_agents():
    """Test multiple agents running concurrently."""
    agents = []
    
    try:
        # Create multiple agents
        for i in range(3):
            agent = GenericPurposeDrivenAgent(
                agent_id=f"agent_{i}",
                purpose=f"Purpose {i}",
                adapter_name="test"
            )
            await agent.initialize()
            agents.append(agent)
        
        # Process events concurrently
        events = [{"type": "test", "id": i} for i in range(3)]
        results = await asyncio.gather(*[
            agent.handle_event(event)
            for agent, event in zip(agents, events)
        ])
        
        assert len(results) == 3
        
    finally:
        # Cleanup all agents
        await asyncio.gather(*[
            agent.cleanup() for agent in agents
        ])


@pytest.mark.asyncio
async def test_error_handling():
    """Test agent error handling."""
    agent = GenericPurposeDrivenAgent(
        agent_id="test",
        purpose="Testing",
        adapter_name="test"
    )
    
    # Mock to raise error
    agent.process_event = AsyncMock(side_effect=ValueError("Test error"))
    
    with pytest.raises(ValueError, match="Test error"):
        await agent.process_event({})
```

## File Locations

### Test Files
- `tests/` - All test files
- `tests/test_perpetual_agents.py` - Perpetual agent tests
- `tests/test_integration.py` - Integration tests
- `tests/test_azure_functions_infrastructure.py` - Azure Functions tests

### Configuration
- `pyproject.toml` - pytest configuration
- `pytest.ini` - Alternative pytest configuration

## Related Skills
- `perpetual-agents` - Testing perpetual agents
- `azure-functions` - Testing Azure Functions
- `mocking-azure` - Mocking Azure services

## Additional Resources
- [pytest-asyncio documentation](https://pytest-asyncio.readthedocs.io/)
- [Python asyncio documentation](https://docs.python.org/3/library/asyncio.html)
- [unittest.mock.AsyncMock](https://docs.python.org/3/library/unittest.mock.html#unittest.mock.AsyncMock)
- tests/ directory - Real-world examples
