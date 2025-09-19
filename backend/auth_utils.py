"""
Authentication utilities for FastAPI integration with Flask auth service.

This module provides token validation and user management for the FastAPI service
by communicating with the Flask authentication service.
"""

import httpx
import os
from typing import Optional, Dict, Any
from functools import wraps
from fastapi import HTTPException, Depends, Header


class AuthService:
    """
    Service for validating user tokens with the Flask auth service.
    """
    
    def __init__(self, auth_service_url: str = "http://localhost:8000"):
        self.auth_service_url = auth_service_url
    
    async def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate a user token with the Flask auth service.
        
        Returns user information if token is valid, None otherwise.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.auth_service_url}/api/validate-token",
                    json={"token": token},
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("valid"):
                        return data
                        
                return None
        except Exception as e:
            print(f"Error validating token: {e}")
            return None
    
    async def get_user_connections(self, user_id: str) -> Dict[str, Any]:
        """
        Get a user's connected services from the auth service.
        """
        # TODO: Implement this endpoint in the Flask auth service
        # For now, return empty connections
        return {"connections": []}


# Global auth service instance
auth_service = AuthService()


async def get_current_user(authorization: str = Header(None)):
    """
    FastAPI dependency to get the current authenticated user.
    
    Expects Authorization header in format: "Bearer <token>"
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Missing Authorization header"
        )
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format. Expected: Bearer <token>"
        )
    
    token = authorization[7:]  # Remove "Bearer " prefix
    
    user_data = await auth_service.validate_token(token)
    
    if not user_data:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )
    
    return user_data["user"]


async def get_current_user_optional(authorization: str = Header(None)):
    """
    FastAPI dependency to get the current user if authenticated, or None.
    
    This doesn't raise an exception if no valid token is provided.
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    token = authorization[7:]
    user_data = await auth_service.validate_token(token)
    
    return user_data["user"] if user_data else None


def require_shared_secret_or_user_token(f):
    """
    Decorator that allows either shared secret (X-Auth) OR user token (Authorization).
    
    This maintains backward compatibility while adding user authentication.
    """
    @wraps(f)
    async def wrapper(*args, **kwargs):
        # This will be handled by FastAPI dependencies
        return await f(*args, **kwargs)
    return wrapper


async def verify_auth_flexible(x_auth: str = Header(None), authorization: str = Header(None)):
    """
    Flexible authentication that accepts either shared secret or user token.
    
    This allows backward compatibility for existing integrations while enabling
    user-specific authentication for new features.
    """
    # Check for user token first
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
        user_data = await auth_service.validate_token(token)
        if user_data:
            return {"type": "user", "user": user_data["user"]}
    
    # Fall back to shared secret
    if x_auth:
        shared_secret = os.environ.get("SHARED_SECRET")
        if shared_secret and x_auth == shared_secret:
            return {"type": "shared_secret"}
    
    raise HTTPException(
        status_code=401,
        detail="Authentication required. Provide either X-Auth header with shared secret or Authorization header with Bearer token."
    )


async def get_user_credentials_for_connector(user_id: str, connector_name: str) -> Optional[Dict[str, Any]]:
    """
    Get stored credentials for a user and connector.
    
    This will query the database through the auth service.
    """
    # TODO: Implement this by calling the Flask auth service
    # For now, return None (no credentials stored)
    return None