"""
Authentication store for CoreAssist Voice Agent.

This module provides an in-memory authentication store with clear TODOs
for database migration when needed.
"""

import os
from typing import Dict, Optional, Any
from datetime import datetime, timedelta


class AuthStore:
    """
    In-memory authentication store for managing user sessions and API credentials.
    
    TODO: Migrate to persistent database storage:
    - Use SQLAlchemy or similar ORM
    - Create tables for users, sessions, and connector_credentials
    - Implement proper password hashing (bcrypt)
    - Add session expiration cleanup
    - Add audit logging for authentication events
    """
    
    def __init__(self):
        # TODO: Replace with database tables
        self.users: Dict[str, Dict[str, Any]] = {}
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.connector_credentials: Dict[str, Dict[str, Dict[str, Any]]] = {}
        
        # Load shared secret from environment
        self.shared_secret = os.environ.get("SHARED_SECRET")
        if not self.shared_secret:
            raise ValueError("SHARED_SECRET environment variable is required")
    
    def verify_shared_secret(self, provided_secret: str) -> bool:
        """Verify the provided shared secret against the configured one."""
        return provided_secret == self.shared_secret
    
    def create_user(self, user_id: str, user_data: Dict[str, Any]) -> None:
        """
        Create a new user in the store.
        
        TODO: Database implementation:
        - Hash passwords with bcrypt
        - Validate user data schema
        - Handle unique constraint violations
        - Add user creation timestamp
        """
        self.users[user_id] = {
            "user_id": user_id,
            "created_at": datetime.utcnow(),
            **user_data
        }
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user data by user ID."""
        return self.users.get(user_id)
    
    def create_session(self, user_id: str, session_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new session for a user.
        
        TODO: Database implementation:
        - Store sessions in database table
        - Implement proper session token generation
        - Add automatic expiration cleanup
        - Add session invalidation on logout
        """
        import uuid
        session_id = str(uuid.uuid4())
        
        self.sessions[session_id] = {
            "session_id": session_id,
            "user_id": user_id,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(hours=24),
            **(session_data or {})
        }
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data by session ID."""
        session = self.sessions.get(session_id)
        
        # Check if session is expired
        if session and session["expires_at"] < datetime.utcnow():
            del self.sessions[session_id]
            return None
        
        return session
    
    def invalidate_session(self, session_id: str) -> bool:
        """Invalidate a session by removing it from the store."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def store_connector_credentials(self, user_id: str, connector_name: str, credentials: Dict[str, Any]) -> None:
        """
        Store connector-specific credentials for a user.
        
        TODO: Database implementation:
        - Encrypt sensitive credential data
        - Use proper key management
        - Add credential rotation support
        - Implement secure credential sharing
        """
        if user_id not in self.connector_credentials:
            self.connector_credentials[user_id] = {}
        
        self.connector_credentials[user_id][connector_name] = {
            "credentials": credentials,
            "stored_at": datetime.utcnow()
        }
    
    def get_connector_credentials(self, user_id: str, connector_name: str) -> Optional[Dict[str, Any]]:
        """Get connector-specific credentials for a user."""
        user_creds = self.connector_credentials.get(user_id, {})
        cred_data = user_creds.get(connector_name)
        
        if cred_data:
            return cred_data["credentials"]
        return None
    
    def delete_connector_credentials(self, user_id: str, connector_name: str) -> bool:
        """Delete connector-specific credentials for a user."""
        user_creds = self.connector_credentials.get(user_id, {})
        if connector_name in user_creds:
            del user_creds[connector_name]
            return True
        return False
    
    def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions from memory.
        
        TODO: Database implementation:
        - Run as background task
        - Add proper logging
        - Consider soft delete with audit trail
        """
        now = datetime.utcnow()
        expired_sessions = [
            session_id for session_id, session in self.sessions.items()
            if session["expires_at"] < now
        ]
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
        
        return len(expired_sessions)
    
    def get_stats(self) -> Dict[str, int]:
        """Get basic statistics about the auth store."""
        return {
            "total_users": len(self.users),
            "active_sessions": len(self.sessions),
            "total_connector_credentials": sum(
                len(user_creds) for user_creds in self.connector_credentials.values()
            )
        }


# Global auth store instance
auth_store = AuthStore()