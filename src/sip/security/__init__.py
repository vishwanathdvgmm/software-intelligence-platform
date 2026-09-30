"""SIP Security — Authentication, Authorization, and Input Validation.

Implements the security architecture from Phase 10:

- **Authentication**: API key-based auth for MVP, extensible to OAuth/OIDC.
- **Authorization**: Role-Based Access Control (RBAC) with least-privilege.
- **Input Validation**: Query sanitization, path traversal protection.
- **Audit Logging**: Structured security event logging.
- **Rate Limiting**: Per-endpoint sliding-window rate limiter.

Security philosophy (Phase 10 §10.2):
    Application Security + Data Security + Infrastructure Security + AI Security
"""

from sip.security.auth import (
    APIKeyAuth,
    AuthResult,
    Role,
    verify_api_key,
)
from sip.security.input_validation import (
    sanitize_query,
    validate_file_path,
    validate_file_upload,
)
from sip.security.middleware import SecurityMiddleware
from sip.security.rate_limiter import RateLimiter

__all__ = [
    "APIKeyAuth",
    "AuthResult",
    "RateLimiter",
    "Role",
    "SecurityMiddleware",
    "sanitize_query",
    "validate_file_path",
    "validate_file_upload",
    "verify_api_key",
]
