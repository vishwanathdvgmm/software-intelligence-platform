"""Authentication and Authorization — Phase 10 §10.5–10.8.

MVP: API key-based authentication with Role-Based Access Control.
Enterprise: Extensible to OAuth/OIDC identity providers.

Principle of Least Privilege (§10.8):
    Each component receives only the minimum required permissions.

Security rules:
    - API keys are NEVER logged in plaintext.
    - Keys are compared using constant-time comparison to prevent timing attacks.
    - Failed authentication attempts are audit-logged.
"""

from __future__ import annotations

import hashlib
import hmac
import os
from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, Field

from sip.core.logging import get_logger

logger = get_logger(__name__)

# ─── Roles (§10.7) ─────────────────────────────────────────────────────────

class Role(StrEnum):
    """RBAC roles as defined in Phase 10 §10.7."""

    ADMIN = "admin"
    EXPERT_MANAGER = "expert_manager"
    DEVELOPER = "developer"
    ANALYST = "analyst"
    VIEWER = "viewer"

# Role hierarchy: higher roles include permissions of lower ones
_ROLE_HIERARCHY: dict[Role, int] = {
    Role.VIEWER: 0,
    Role.ANALYST: 1,
    Role.DEVELOPER: 2,
    Role.EXPERT_MANAGER: 3,
    Role.ADMIN: 4,
}

class AuthResult(BaseModel):
    """Result of an authentication attempt."""

    authenticated: bool = False
    user_id: str = ""
    role: Role = Role.VIEWER
    error: str | None = None

class APIKeyAuth:
    """API key authentication provider.

    Keys are stored as SHA-256 hashes — the raw key is never persisted.
    In production, keys should come from an external secret store; this
    in-memory store is for the MVP.
    """

    def __init__(self) -> None:
        # Map of key_hash -> (user_id, role)
        self._key_store: dict[str, tuple[str, Role]] = {}

    @staticmethod
    def _hash_key(key: str) -> str:
        """Hash an API key using SHA-256."""
        return hashlib.sha256(key.encode("utf-8")).hexdigest()

    def register_key(self, key: str, user_id: str, role: Role = Role.VIEWER) -> None:
        """Register an API key (stores the hash, not the raw key)."""
        key_hash = self._hash_key(key)
        self._key_store[key_hash] = (user_id, role)
        logger.info(
            "auth.key_registered",
            user_id=user_id,
            role=role.value,
            # Never log the key itself
        )

    def authenticate(self, key: str) -> AuthResult:
        """Authenticate using an API key (constant-time comparison)."""
        key_hash = self._hash_key(key)

        for stored_hash, (user_id, role) in self._key_store.items():
            if hmac.compare_digest(key_hash, stored_hash):
                logger.info(
                    "auth.success",
                    user_id=user_id,
                    role=role.value,
                )
                return AuthResult(
                    authenticated=True,
                    user_id=user_id,
                    role=role,
                )

        # Audit log the failure — but never log the attempted key
        logger.warning("auth.failed", reason="invalid_api_key")
        return AuthResult(authenticated=False, error="Invalid API key")

    def has_permission(self, role: Role, required_role: Role) -> bool:
        """Check if a role meets the minimum required role level."""
        return _ROLE_HIERARCHY.get(role, -1) >= _ROLE_HIERARCHY.get(required_role, 99)

# ─── Module-level convenience ──────────────────────────────────────────────

_auth: APIKeyAuth | None = None

def get_auth() -> APIKeyAuth:
    """Return the global API key auth provider (lazy singleton)."""
    global _auth
    if _auth is None:
        _auth = APIKeyAuth()
        # Register a development key from environment if available
        dev_key = os.environ.get("SIP_API_KEY")
        if dev_key:
            _auth.register_key(dev_key, user_id="dev-user", role=Role.ADMIN)
    return _auth

def verify_api_key(key: str) -> AuthResult:
    """Convenience wrapper for API key verification."""
    return get_auth().authenticate(key)
