"""Tests for AOSAuth authentication and access control."""

import pytest

from aos_client.auth import AOSAuth, TokenClaims


class TestAOSAuth:
    """AOSAuth unit tests."""

    def test_init_defaults(self):
        auth = AOSAuth()
        assert auth.tenant_id is None
        assert auth.client_id is None
        assert auth.audience is None
        assert auth.allowed_roles == ["Workflows.Execute"]

    def test_init_custom(self):
        auth = AOSAuth(
            tenant_id="tenant-123",
            client_id="client-456",
            audience="api://custom",
            allowed_roles=["Admin", "User"],
        )
        assert auth.tenant_id == "tenant-123"
        assert auth.client_id == "client-456"
        assert auth.audience == "api://custom"
        assert auth.allowed_roles == ["Admin", "User"]

    def test_default_audience(self):
        auth = AOSAuth(client_id="my-app")
        assert auth.audience == "api://my-app"

    def test_require_role_success(self):
        auth = AOSAuth()
        claims = TokenClaims(
            subject="user-1",
            audience="test",
            issuer="test",
            roles=["Workflows.Execute", "Admin"],
        )
        # Should not raise
        auth.require_role(claims, "Admin")

    def test_require_role_failure(self):
        auth = AOSAuth()
        claims = TokenClaims(
            subject="user-1",
            audience="test",
            issuer="test",
            roles=["Reader"],
        )
        with pytest.raises(PermissionError, match="missing required role"):
            auth.require_role(claims, "Admin")

    def test_require_any_allowed_role_success(self):
        auth = AOSAuth(allowed_roles=["Admin", "Workflows.Execute"])
        claims = TokenClaims(
            subject="user-1",
            audience="test",
            issuer="test",
            roles=["Workflows.Execute"],
        )
        # Should not raise
        auth.require_any_allowed_role(claims)

    def test_require_any_allowed_role_failure(self):
        auth = AOSAuth(allowed_roles=["Admin"])
        claims = TokenClaims(
            subject="user-1",
            audience="test",
            issuer="test",
            roles=["Reader"],
        )
        with pytest.raises(PermissionError, match="missing any of allowed roles"):
            auth.require_any_allowed_role(claims)

    def test_extract_bearer_token(self):
        auth = AOSAuth()
        assert auth.extract_bearer_token("Bearer abc123") == "abc123"
        assert auth.extract_bearer_token("bearer ABC") == "ABC"
        assert auth.extract_bearer_token("Basic xyz") is None
        assert auth.extract_bearer_token(None) is None
        assert auth.extract_bearer_token("") is None

    @pytest.mark.asyncio
    async def test_validate_token_dev_mode(self):
        """In dev mode (no tenant/client), returns default claims."""
        auth = AOSAuth()
        claims = await auth.validate_token("fake.token.here")
        assert claims.subject == "dev-user"
        assert "Workflows.Execute" in claims.roles


class TestTokenClaims:
    """TokenClaims unit tests."""

    def test_create_minimal(self):
        claims = TokenClaims(subject="sub", audience="aud", issuer="iss")
        assert claims.subject == "sub"
        assert claims.roles == []
        assert claims.scopes == []
        assert claims.app_id is None

    def test_create_full(self):
        claims = TokenClaims(
            subject="user-1",
            audience="api://my-app",
            issuer="https://login.microsoftonline.com/tenant/v2.0",
            roles=["Admin", "Workflows.Execute"],
            scopes=["read", "write"],
            app_id="app-123",
            tenant_id="tenant-456",
            name="John Doe",
            raw={"custom": "data"},
        )
        assert claims.name == "John Doe"
        assert len(claims.roles) == 2
        assert claims.raw["custom"] == "data"
