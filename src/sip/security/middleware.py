"""Security Middleware — Phase 10 §10.23.

Implements API Security at the FastAPI boundary:
    - Authentication (API Key)
    - Rate Limiting

By default, we enforce rate limiting on all routes. Authentication can be
enforced globally or selectively (here we enforce it globally except for /api/health and /api/metrics).
"""

from __future__ import annotations

import json
from typing import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from sip.core.logging import get_logger
from sip.security.auth import get_auth
from sip.security.rate_limiter import get_rate_limiter

logger = get_logger(__name__)

# Endpoints that bypass authentication (public endpoints)
PUBLIC_ENDPOINTS = {
    "/api/health",
    "/api/metrics",
    "/api/chat",
    "/api/knowledge/stats",
}

class SecurityMiddleware(BaseHTTPMiddleware):
    """FastAPI Middleware for Rate Limiting and Authentication."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        
        path = request.url.path

        # 1. Rate Limiting (§10.24)
        client_ip = request.client.host if request.client else "unknown"
        # We use IP as the default rate limit key for MVP.
        # In a real app, it could be the API key or User ID.
        rate_limiter = get_rate_limiter()
        if not rate_limiter.check_limit(key=client_ip, endpoint=path):
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded"},
            )

        # 2. Authentication (§10.5)
        if path not in PUBLIC_ENDPOINTS:
            # Check for API key in header
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                logger.warning("security.auth_missing", path=path, ip=client_ip)
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Missing or invalid Authorization header"},
                    headers={"WWW-Authenticate": "Bearer"},
                )

            api_key = auth_header.split(" ")[1]
            auth = get_auth()
            auth_result = auth.authenticate(api_key)

            if not auth_result.authenticated:
                return JSONResponse(
                    status_code=401,
                    content={"detail": auth_result.error or "Invalid API key"},
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Optionally attach auth_result to request state for downstream use
            request.state.auth_result = auth_result

        # Proceed with the request
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            # 3. Error Handling (§10.38)
            # Catch unhandled exceptions at the boundary so we don't leak stack traces
            logger.exception("security.unhandled_exception", path=path, error=str(e))
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"},
            )
