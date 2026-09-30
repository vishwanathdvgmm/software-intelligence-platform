"""Rate Limiting — Phase 10 §10.24-10.25.

Provides a simple in-memory sliding-window rate limiter for the MVP.
In a production deployment, this would be backed by Redis (using sip.core.config.RedisConfig).
"""

from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass
from typing import Optional

from sip.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class RateLimitConfig:
    """Rate limit configuration."""
    requests: int = 100
    window_seconds: int = 60


class RateLimiter:
    """Sliding window rate limiter (In-Memory).
    
    Protects the API, LLM Gateway, and Tool Runtime against abuse (§10.25).
    """

    def __init__(self, default_config: RateLimitConfig | None = None) -> None:
        self.default_config = default_config or RateLimitConfig()
        # endpoint -> key -> list of timestamps
        self._windows: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
        # endpoint -> specific config
        self._configs: dict[str, RateLimitConfig] = {}

    def configure_endpoint(self, endpoint: str, config: RateLimitConfig) -> None:
        """Set a specific rate limit for an endpoint."""
        self._configs[endpoint] = config

    def check_limit(self, key: str, endpoint: str = "default") -> bool:
        """Check if the key has exceeded the rate limit.
        
        Returns True if allowed, False if rate limited.
        """
        config = self._configs.get(endpoint, self.default_config)
        now = time.time()
        window_start = now - config.window_seconds

        # Get window for this endpoint/key
        timestamps = self._windows[endpoint][key]

        # Evict old timestamps
        # Fast eviction for MVP
        while timestamps and timestamps[0] < window_start:
            timestamps.pop(0)

        # Check limit
        if len(timestamps) >= config.requests:
            logger.warning(
                "security.rate_limit_exceeded",
                key=key,
                endpoint=endpoint,
                limit=config.requests,
                window=config.window_seconds,
            )
            return False

        # Allow and record
        timestamps.append(now)
        return True

    def clear(self) -> None:
        """Clear all rate limit data."""
        self._windows.clear()


# Global rate limiter instance
_rate_limiter = RateLimiter()

def get_rate_limiter() -> RateLimiter:
    return _rate_limiter
