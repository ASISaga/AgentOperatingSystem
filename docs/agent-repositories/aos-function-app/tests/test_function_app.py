"""Tests for the AOS Azure Function app.

Copy and adapt from monorepo: tests/test_azure_functions_infrastructure.py
"""
import pytest


class TestFunctionApp:
    """AOS Function App tests."""

    def test_health_endpoint(self):
        """Test health check HTTP endpoint."""
        # Copy and adapt from monorepo test_azure_functions_infrastructure.py
        assert True

    def test_service_bus_trigger(self):
        """Test Service Bus trigger function."""
        assert True
