"""
Pytest configuration and shared fixtures for cfo-agent tests.
"""

import pytest
from cfo_agent import CFOAgent


@pytest.fixture
def agent_id() -> str:
    return "cfo-test-001"


@pytest.fixture
def basic_cfo(agent_id: str) -> CFOAgent:
    """Return an uninitialised CFOAgent instance with defaults."""
    return CFOAgent(agent_id=agent_id)


@pytest.fixture
async def initialised_cfo(basic_cfo: CFOAgent) -> CFOAgent:
    """Return an initialised CFOAgent instance."""
    await basic_cfo.initialize()
    return basic_cfo
