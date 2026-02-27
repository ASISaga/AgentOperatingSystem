"""
Pytest configuration and shared fixtures for purpose-driven-agent tests.
"""

import pytest
from purpose_driven_agent import GenericPurposeDrivenAgent


@pytest.fixture
def agent_id() -> str:
    """Return a deterministic agent ID for tests."""
    return "test-agent-001"


@pytest.fixture
def basic_agent(agent_id: str) -> GenericPurposeDrivenAgent:
    """Return an uninitialised GenericPurposeDrivenAgent instance."""
    return GenericPurposeDrivenAgent(
        agent_id=agent_id,
        purpose="Test purpose for unit testing",
        purpose_scope="Testing scope",
        adapter_name="test-adapter",
    )


@pytest.fixture
async def initialised_agent(basic_agent: GenericPurposeDrivenAgent) -> GenericPurposeDrivenAgent:
    """Return an initialised GenericPurposeDrivenAgent instance."""
    await basic_agent.initialize()
    return basic_agent
