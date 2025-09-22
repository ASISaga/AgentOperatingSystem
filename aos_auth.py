"""
AgentOperatingSystem Unified Authentication System
- Azure B2C authentication
- LinkedIn OAuth integration
- JWT validation and token management
- Multi-provider authentication support
"""
import os, json, requests
from typing import Dict, Any, Optional
from msal import ConfidentialClientApplication
from jwt.algorithms import RSAAlgorithm
import jwt

class UnifiedAuthHandler:
    UNAUTHORIZED_MSG = "Unauthorized"
    def __init__(self):
        # Azure B2C Configuration
        self.TENANT = os.getenv("B2C_TENANT")
        self.POLICY = os.getenv("B2C_POLICY") 
        self.CLIENTID = os.getenv("B2CCLIENT_ID")
        self.CLIENTSECRET = os.getenv("B2CCLIENT_SECRET")
        self.SCOPE = [os.getenv("B2CAPISCOPE")] if os.getenv("B2CAPISCOPE") else []
        self.ISSUER = os.getenv("B2C_ISSUER")
        self.AUTHORITY = f"https://{self.TENANT}/{self.POLICY}" if self.TENANT and self.POLICY else None
        # LinkedIn OAuth Configuration
        self.LINKEDIN_CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
        self.LINKEDIN_CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
        self.LINKEDIN_REDIRECT_URI = os.getenv("LINKEDIN_REDIRECT_URI")
        self._jwks = None
    def login(self, username: str, password: str) -> Dict[str, Any]:
        if not username or not password:
            return {"error": "username & password required", "status": 400}
        if not self.AUTHORITY or not self.CLIENTID or not self.CLIENTSECRET:
            return {"error": "B2C configuration missing", "status": 500}
        try:
            app = ConfidentialClientApplication(
                self.CLIENTID, 
                authority=self.AUTHORITY, 
                client_credential=self.CLIENTSECRET
            )
            result = app.acquire_token_by_username_password(
                username=username, 
                password=password, 
                scopes=self.SCOPE
            )
            if "access_token" in result:
                return {
                    "accesstoken": result["access_token"],
                    "refreshtoken": result.get("refresh_token"),
                    "expiresin": result["expires_in"],
                    "status": 200
                }
            return {"error": result, "status": 400}
        except Exception as e:
            return {"error": f"Authentication failed: {str(e)}", "status": 500}
    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        if not refresh_token:
            return {"error": "refreshtoken required", "status": 400}
        if not self.AUTHORITY or not self.CLIENTID or not self.CLIENTSECRET:
            return {"error": "B2C configuration missing", "status": 500}
        try:
            app = ConfidentialClientApplication(
                self.CLIENTID, 
                authority=self.AUTHORITY, 
                client_credential=self.CLIENTSECRET
            )
            result = app.acquire_token_by_refresh_token(refresh_token, scopes=self.SCOPE)
            if "access_token" in result:
                return {
                    "accesstoken": result["access_token"],
                    "refreshtoken": result.get("refresh_token"),
                    "expiresin": result["expires_in"],
                    "status": 200
                }
            return {"error": result, "status": 400}
        except Exception as e:
            return {"error": f"Token refresh failed: {str(e)}", "status": 500}
    def load_jwks(self) -> Dict[str, Any]:
        if not self._jwks and self.TENANT and self.POLICY:
            try:
                url = f"https://{self.TENANT}/discovery/v2.0/keys?p={self.POLICY}"
                response = requests.get(url)
                response.raise_for_status()
                self._jwks = response.json()
            except Exception as e:
                print(f"Warning: Failed to load JWKS: {e}")
                return {"keys": []}
        return self._jwks or {"keys": []}
    def validate_jwt(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            header = jwt.get_unverified_header(token)
            jwks = self.load_jwks()["keys"]
            key = next((k for k in jwks if k["kid"] == header["kid"]), None)
            if not key:
                return None
            pub = RSAAlgorithm.from_jwk(json.dumps(key))
            claims = jwt.decode(
                token, 
                pub,
                algorithms=[header["alg"]],
                audience=self.CLIENTID,
                issuer=self.ISSUER
            )
            return claims
        except Exception as e:
            print(f"JWT validation failed: {e}")
            return None
    def linkedin_auth_url(self, state: str = None) -> str:
        if not self.LINKEDIN_CLIENT_ID or not self.LINKEDIN_REDIRECT_URI:
            raise ValueError("LinkedIn configuration missing")
        base_url = "https://www.linkedin.com/oauth/v2/authorization"
        params = {
            "response_type": "code",
            "client_id": self.LINKEDIN_CLIENT_ID,
            "redirect_uri": self.LINKEDIN_REDIRECT_URI,
            "scope": "openid profile email"
        }
        if state:
            params["state"] = state
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{query_string}"
    def linkedin_exchange_code(self, code: str) -> Dict[str, Any]:
        if not self.LINKEDIN_CLIENT_ID or not self.LINKEDIN_CLIENT_SECRET:
            return {"error": "LinkedIn configuration missing", "status": 500}
        try:
            token_url = "https://www.linkedin.com/oauth/v2/accessToken"
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "client_id": self.LINKEDIN_CLIENT_ID,
                "client_secret": self.LINKEDIN_CLIENT_SECRET,
                "redirect_uri": self.LINKEDIN_REDIRECT_URI
            }
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            token_data = response.json()
            profile_url = "https://api.linkedin.com/v2/userinfo"
            headers = {"Authorization": f"Bearer {token_data['access_token']}"}
            profile_response = requests.get(profile_url, headers=headers)
            profile_response.raise_for_status()
            profile_data = profile_response.json()
            return {
                "access_token": token_data["access_token"],
                "profile": profile_data,
                "email": profile_data.get("email"),
                "status": 200
            }
        except Exception as e:
            return {"error": f"LinkedIn authentication failed: {str(e)}", "status": 500}
    def validate_configuration(self) -> Dict[str, Any]:
        issues = []
        if not self.TENANT:
            issues.append("Missing B2C_TENANT")
        if not self.POLICY:
            issues.append("Missing B2C_POLICY")
        if not self.CLIENTID:
            issues.append("Missing B2CCLIENT_ID")
        if not self.CLIENTSECRET:
            issues.append("Missing B2CCLIENT_SECRET")
        linkedin_configured = bool(
            self.LINKEDIN_CLIENT_ID and 
            self.LINKEDIN_CLIENT_SECRET and 
            self.LINKEDIN_REDIRECT_URI
        )
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "b2c_configured": bool(self.TENANT and self.POLICY and self.CLIENTID and self.CLIENTSECRET),
            "linkedin_configured": linkedin_configured,
            "jwks_loaded": bool(self._jwks)
        }

# Singleton instance
auth_handler = UnifiedAuthHandler()

__all__ = ['auth_handler', 'UnifiedAuthHandler']
