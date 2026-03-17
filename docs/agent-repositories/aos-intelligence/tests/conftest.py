"""
Pytest configuration and shared fixtures for aos-intelligence tests.
"""

import pytest
from aos_intelligence.config import MLConfig


@pytest.fixture
def ml_config():
    """Default MLConfig for tests."""
    return MLConfig(
        enable_training=True,
        enable_dpo=True,
        enable_lorax=True,
        enable_foundry_agent_service=False,
        model_storage_path="/tmp/test_models",
        training_data_path="/tmp/test_data",
        preference_data_path="/tmp/test_preferences",
    )


@pytest.fixture
def minimal_config():
    """Minimal MLConfig with most features disabled."""
    return MLConfig(
        enable_training=False,
        enable_dpo=False,
        enable_lorax=False,
        enable_foundry_agent_service=False,
    )
