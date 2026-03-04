"""
Pytest configuration and shared fixtures for cso-agent tests.
"""

import pytest
from cso_agent import CSOAgent


@pytest.fixture
def agent_id() -> str:
    return "cso-test-001"


@pytest.fixture
def basic_cso(agent_id: str) -> CSOAgent:
    """Return an uninitialised CSOAgent instance with defaults."""
    return CSOAgent(agent_id=agent_id)


@pytest.fixture
async def initialised_cso(basic_cso: CSOAgent) -> CSOAgent:
    """Return an initialised CSOAgent instance."""
    await basic_cso.initialize()
    return basic_cso
