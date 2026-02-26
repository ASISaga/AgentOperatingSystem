"""
Pytest configuration and shared fixtures for cmo-agent tests.
"""

import pytest
from cmo_agent import CMOAgent


@pytest.fixture
def agent_id() -> str:
    return "cmo-test-001"


@pytest.fixture
def basic_cmo(agent_id: str) -> CMOAgent:
    """Return an uninitialised CMOAgent instance with defaults."""
    return CMOAgent(agent_id=agent_id)


@pytest.fixture
async def initialised_cmo(basic_cmo: CMOAgent) -> CMOAgent:
    """Return an initialised CMOAgent instance."""
    await basic_cmo.initialize()
    return basic_cmo
