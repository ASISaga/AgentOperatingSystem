"""
Pytest configuration and shared fixtures for ceo-agent tests.
"""

import pytest
from ceo_agent import CEOAgent


@pytest.fixture
def agent_id() -> str:
    return "ceo-test-001"


@pytest.fixture
def basic_ceo(agent_id: str) -> CEOAgent:
    """Return an uninitialised CEOAgent instance with defaults."""
    return CEOAgent(agent_id=agent_id)


@pytest.fixture
async def initialised_ceo(basic_ceo: CEOAgent) -> CEOAgent:
    """Return an initialised CEOAgent instance."""
    await basic_ceo.initialize()
    return basic_ceo
