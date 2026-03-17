"""
Pytest configuration and shared fixtures for leadership-agent tests.
"""

import pytest
from leadership_agent import LeadershipAgent


@pytest.fixture
def agent_id() -> str:
    return "leadership-test-001"


@pytest.fixture
def basic_agent(agent_id: str) -> LeadershipAgent:
    """Return an uninitialised LeadershipAgent instance."""
    return LeadershipAgent(
        agent_id=agent_id,
        name="Test Leader",
    )


@pytest.fixture
async def initialised_agent(basic_agent: LeadershipAgent) -> LeadershipAgent:
    """Return an initialised LeadershipAgent instance."""
    await basic_agent.initialize()
    return basic_agent
