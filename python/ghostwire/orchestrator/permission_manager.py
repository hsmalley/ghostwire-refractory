"""
GhostWire Openspec Orchestrator - Permission Manager

Implements the Permission Manager component that handles access control
and permissions for tasks executed by the orchestration system.
"""

import logging
import secrets
from datetime import datetime, timedelta
from typing import Any


class PermissionManager:
    def __init__(self):
        """
        Initialize the Permission Manager.

        Sets up default permissions and access control mechanisms.
        """
        self.logger = logging.getLogger(__name__)
        self.permissions = {}
        self.sessions = {}

        # Define default permission levels
        self.permission_levels = {"read": 1, "write": 2, "execute": 3, "admin": 4}

        # Set up default permissions for different task types
        self.default_permissions = {
            "chat": "read",
            "embed": "read",
            "summarize": "read",
            "retrieval": "read",
            "code_generation": "write",
            "benchmark": "execute",
            "analysis": "read",
            "patch_application": "admin",
        }

    def check_permission(
        self, task: dict[str, Any], context: dict[str, Any] | None = None
    ) -> bool:
        """
        Check if the current context has permission to execute a task.

        Args:
            task: The task to check permissions for
            context: Context information including user/session details

        Returns:
            True if permission is granted, False otherwise
        """
        # Extract task information
        task_type = task.get("type", "unknown")

        # Get the required permission level for this task type
        required_level = self.default_permissions.get(task_type, "read")
        required_level_value = self.permission_levels.get(required_level, 1)

        # Get user's permission level from context
        user_level = context.get("permission_level", "read") if context else "read"
        user_level_value = self.permission_levels.get(user_level, 1)

        # Check if user has sufficient permissions
        has_permission = user_level_value >= required_level_value

        self.logger.info(
            f"Permission check for task {task_type}: "
            f"required={required_level}({required_level_value}), "
            f"user={user_level}({user_level_value}), "
            f"granted={has_permission}"
        )

        return has_permission

    def grant_permission(
        self, user_id: str, permission_level: str, duration_minutes: int = 60
    ) -> str:
        """
        Grant temporary permissions to a user.

        Args:
            user_id: ID of the user
            permission_level: Level of permission to grant
            duration_minutes: Duration for which to grant permission

        Returns:
            Session token for the granted permission
        """
        if permission_level not in self.permission_levels:
            raise ValueError(f"Invalid permission level: {permission_level}")

        # Generate a unique session token
        session_token = secrets.token_urlsafe(32)

        # Store session information
        session_info = {
            "user_id": user_id,
            "permission_level": permission_level,
            "permission_level_value": self.permission_levels[permission_level],
            "granted_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(minutes=duration_minutes),
        }

        self.sessions[session_token] = session_info

        self.logger.info(
            f"Granted {permission_level} permissions to user {user_id} for {duration_minutes} minutes"
        )

        return session_token

    def revoke_permission(self, session_token: str) -> bool:
        """
        Revoke permissions for a session.

        Args:
            session_token: Session token to revoke

        Returns:
            True if successfully revoked, False otherwise
        """
        if session_token in self.sessions:
            del self.sessions[session_token]
            self.logger.info(f"Revoked permissions for session: {session_token}")
            return True
        return False

    def validate_session(self, session_token: str) -> dict[str, Any]:
        """
        Validate if a session token is still valid.

        Args:
            session_token: Session token to validate

        Returns:
            Dictionary with validation results
        """
        if session_token not in self.sessions:
            return {"valid": False, "reason": "Session token not found"}

        session_info = self.sessions[session_token]
        current_time = datetime.now()

        if current_time > session_info["expires_at"]:
            del self.sessions[session_token]  # Clean up expired session
            return {"valid": False, "reason": "Session has expired"}

        return {
            "valid": True,
            "user_id": session_info["user_id"],
            "permission_level": session_info["permission_level"],
            "expires_at": session_info["expires_at"],
        }

    def create_context_with_session(self, session_token: str) -> dict[str, Any] | None:
        """
        Create a context dictionary based on a session token.

        Args:
            session_token: Session token to create context from

        Returns:
            Context dictionary or None if session is invalid
        """
        validation = self.validate_session(session_token)

        if not validation["valid"]:
            return None

        return {
            "user_id": validation["user_id"],
            "permission_level": validation["permission_level"],
            "session_token": session_token,
        }

    def register_custom_permission(self, task_type: str, required_permission: str):
        """
        Register a custom permission requirement for a task type.

        Args:
            task_type: Type of task
            required_permission: Required permission level
        """
        self.default_permissions[task_type] = required_permission
        self.logger.info(
            f"Registered custom permission: {task_type} requires {required_permission}"
        )

    def get_user_permissions(self, user_id: str) -> dict[str, Any]:
        """
        Get all active permissions for a user.

        Args:
            user_id: ID of the user

        Returns:
            Dictionary with user's active permissions
        """
        user_sessions = {}
        current_time = datetime.now()

        for token, session_info in self.sessions.items():
            if (
                session_info["user_id"] == user_id
                and current_time <= session_info["expires_at"]
            ):
                user_sessions[token] = {
                    "permission_level": session_info["permission_level"],
                    "granted_at": session_info["granted_at"],
                    "expires_at": session_info["expires_at"],
                }

        return user_sessions
