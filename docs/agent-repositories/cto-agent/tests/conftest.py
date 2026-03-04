"""
Pytest configuration and shared fixtures for cto-agent tests.
"""

import pytest
from cto_agent import CTOAgent


@pytest.fixture
def agent_id() -> str:
    return "cto-test-001"


@pytest.fixture
def basic_cto(agent_id: str) -> CTOAgent:
    """Return an uninitialised CTOAgent instance with defaults."""
    return CTOAgent(agent_id=agent_id)


@pytest.fixture
async def initialised_cto(basic_cto: CTOAgent) -> CTOAgent:
    """Return an initialised CTOAgent instance."""
    await basic_cto.initialize()
    return basic_cto
