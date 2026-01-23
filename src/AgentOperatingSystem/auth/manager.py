"""
AOS Authentication Manager

Unified authentication system for AOS supporting multiple providers.
"""

import logging
import os
import jwt
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from ..config.auth import AuthConfig


class AuthenticationError(Exception):
    """Authentication-related errors"""
    pass


class AuthManager:
    """
    Unified authentication manager for AOS.

    Supports:
    - Azure B2C authentication
    - OAuth providers (LinkedIn, etc.)
    - JWT token validation
    - Session management
    """

    def __init__(self, config: AuthConfig):
        self.config = config
        self.logger = logging.getLogger("AOS.AuthManager")

        # Active sessions
        self.sessions = {}

        # Provider configurations
        self.providers = {
            "azure_b2c": self._configure_azure_b2c(),
            "oauth": self._configure_oauth(),
            "jwt": self._configure_jwt()
        }

        self.logger.info(f"AuthManager initialized with provider: {config.auth_provider}")

    def _configure_azure_b2c(self) -> Dict[str, Any]:
        """Configure Azure B2C authentication"""
        return {
            "tenant": os.getenv("B2C_TENANT"),
            "policy": os.getenv("B2C_POLICY"),
            "client_id": os.getenv("B2C_CLIENT_ID"),
            "client_secret": os.getenv("B2C_CLIENT_SECRET"),
            "scope": os.getenv("B2C_SCOPE", "").split(",") if os.getenv("B2C_SCOPE") else []
        }

    def _configure_oauth(self) -> Dict[str, Any]:
        """Configure OAuth providers"""
        return {
            "linkedin": {
                "client_id": os.getenv("LINKEDIN_CLIENT_ID"),
                "client_secret": os.getenv("LINKEDIN_CLIENT_SECRET"),
                "redirect_uri": os.getenv("LINKEDIN_REDIRECT_URI")
            }
        }

    def _configure_jwt(self) -> Dict[str, Any]:
        """Configure JWT validation"""
        return {
            "secret": os.getenv("JWT_SECRET", "default_secret"),
            "algorithm": "HS256",
            "expiration_hours": 24
        }

    async def authenticate(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        Authenticate user with provided credentials.

        Args:
            credentials: Authentication credentials

        Returns:
            Authentication result with token or error
        """
        if not self.config.enable_auth:
            # Authentication disabled - return success
            return {
                "success": True,
                "token": "auth_disabled",
                "user": {"id": "anonymous", "role": "user"}
            }

        try:
            auth_type = credentials.get("type", self.config.auth_provider)

            if auth_type == "azure_b2c":
                return await self._authenticate_azure_b2c(credentials)
            elif auth_type == "oauth":
                return await self._authenticate_oauth(credentials)
            elif auth_type == "jwt":
                return await self._authenticate_jwt(credentials)
            else:
                raise AuthenticationError(f"Unsupported authentication type: {auth_type}")

        except Exception as e:
            self.logger.error(f"Authentication failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validate an authentication token.

        Args:
            token: Token to validate

        Returns:
            Validation result with user info or error
        """
        if not self.config.enable_auth or token == "auth_disabled":
            return {
                "valid": True,
                "user": {"id": "anonymous", "role": "user"}
            }

        try:
            # Check if token is in active sessions
            if token in self.sessions:
                session = self.sessions[token]
                if session["expires_at"] > datetime.utcnow():
                    return {
                        "valid": True,
                        "user": session["user"]
                    }
                else:
                    # Remove expired session
                    del self.sessions[token]

            # Validate JWT token
            jwt_config = self.providers["jwt"]
            payload = jwt.decode(
                token,
                jwt_config["secret"],
                algorithms=[jwt_config["algorithm"]]
            )

            return {
                "valid": True,
                "user": payload.get("user", {})
            }

        except jwt.ExpiredSignatureError:
            return {"valid": False, "error": "Token expired"}
        except jwt.InvalidTokenError:
            return {"valid": False, "error": "Invalid token"}
        except Exception as e:
            self.logger.error(f"Token validation failed: {e}")
            return {"valid": False, "error": str(e)}

    async def create_session(self, user: Dict[str, Any]) -> str:
        """
        Create a new user session.

        Args:
            user: User information

        Returns:
            Session token
        """
        # Generate JWT token
        jwt_config = self.providers["jwt"]

        payload = {
            "user": user,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=jwt_config["expiration_hours"])
        }

        token = jwt.encode(payload, jwt_config["secret"], algorithm=jwt_config["algorithm"])

        # Store session
        self.sessions[token] = {
            "user": user,
            "created_at": datetime.utcnow(),
            "expires_at": payload["exp"]
        }

        self.logger.info(f"Created session for user: {user.get('id', 'unknown')}")
        return token

    async def revoke_session(self, token: str) -> bool:
        """
        Revoke a user session.

        Args:
            token: Session token to revoke

        Returns:
            Success status
        """
        if token in self.sessions:
            del self.sessions[token]
            self.logger.info("Session revoked")
            return True

        return False

    def get_auth_status(self) -> Dict[str, Any]:
        """Get authentication system status"""
        return {
            "enabled": self.config.enable_auth,
            "provider": self.config.auth_provider,
            "active_sessions": len(self.sessions),
            "providers_configured": {
                provider: bool(config.get("client_id") or config.get("secret"))
                for provider, config in self.providers.items()
            }
        }

    async def _authenticate_azure_b2c(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Authenticate using Azure B2C"""
        # Placeholder for Azure B2C authentication
        username = credentials.get("username")
        password = credentials.get("password")

        if not username or not password:
            raise AuthenticationError("Username and password required")

        # Simulate authentication
        user = {
            "id": username,
            "email": username,
            "provider": "azure_b2c",
            "role": "user"
        }

        token = await self.create_session(user)

        return {
            "success": True,
            "token": token,
            "user": user
        }

    def get_linkedin_auth_url(self, state: str = None) -> str:
        """
        Generate LinkedIn OAuth authorization URL.
        Enhanced from old aos_auth.py functionality.
        """
        linkedin_config = self.providers["oauth"]["linkedin"]

        if not linkedin_config["client_id"] or not linkedin_config["redirect_uri"]:
            raise AuthenticationError("LinkedIn configuration missing")

        base_url = "https://www.linkedin.com/oauth/v2/authorization"
        params = {
            "response_type": "code",
            "client_id": linkedin_config["client_id"],
            "redirect_uri": linkedin_config["redirect_uri"],
            "scope": "openid profile email"
        }

        if state:
            params["state"] = state

        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{query_string}"

    async def exchange_linkedin_code(self, code: str) -> Dict[str, Any]:
        """
        Exchange LinkedIn OAuth code for access token and user profile.
        Enhanced from old aos_auth.py functionality.
        """
        linkedin_config = self.providers["oauth"]["linkedin"]

        if not linkedin_config["client_id"] or not linkedin_config["client_secret"]:
            raise AuthenticationError("LinkedIn configuration missing")

        try:
            import requests

            # Exchange code for access token
            token_url = "https://www.linkedin.com/oauth/v2/accessToken"
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "client_id": linkedin_config["client_id"],
                "client_secret": linkedin_config["client_secret"],
                "redirect_uri": linkedin_config["redirect_uri"]
            }

            response = requests.post(token_url, data=data)
            response.raise_for_status()
            token_data = response.json()

            # Get user profile
            profile_url = "https://api.linkedin.com/v2/userinfo"
            headers = {"Authorization": f"Bearer {token_data['access_token']}"}
            profile_response = requests.get(profile_url, headers=headers)
            profile_response.raise_for_status()
            profile_data = profile_response.json()

            # Create user session
            user = {
                "id": profile_data.get("sub"),
                "email": profile_data.get("email"),
                "name": profile_data.get("name"),
                "provider": "linkedin",
                "role": "user"
            }

            session_token = await self.create_session(user)

            return {
                "success": True,
                "access_token": token_data["access_token"],
                "session_token": session_token,
                "user": user,
                "profile": profile_data
            }

        except Exception as e:
            self.logger.error(f"LinkedIn authentication failed: {e}")
            raise AuthenticationError(f"LinkedIn authentication failed: {str(e)}")

    async def _authenticate_oauth(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Authenticate using OAuth provider"""
        provider = credentials.get("provider", "linkedin")
        code = credentials.get("code")

        if not code:
            raise AuthenticationError("OAuth code required")

        # Use LinkedIn-specific authentication
        if provider == "linkedin":
            return await self.exchange_linkedin_code(code)

        # Fallback for other providers
        user = {
            "id": f"{provider}_user",
            "provider": provider,
            "role": "user"
        }

        token = await self.create_session(user)

        return {
            "success": True,
            "token": token,
            "user": user
        }

    async def _authenticate_jwt(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Authenticate using JWT token"""
        token = credentials.get("token")

        if not token:
            raise AuthenticationError("JWT token required")

        validation_result = await self.validate_token(token)

        if validation_result["valid"]:
            return {
                "success": True,
                "token": token,
                "user": validation_result["user"]
            }
        else:
            raise AuthenticationError(validation_result.get("error", "Invalid token"))
