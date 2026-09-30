"""LLM Gateway — M6 implementation.

The central router and resilience layer for all LLM interactions.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator

from sip.core.contracts.llm import LLMProvider, LLMRequest, LLMResponse
from sip.core.errors import ConfigurationError, LLMError, LLMProviderError
from sip.core.protocols.llm import LLMProviderAdapter

logger = logging.getLogger(__name__)

class CentralLLMGateway:
    """Implements the LLMGateway protocol.

    Handles routing to the appropriate provider adapter.
    """

    def __init__(self) -> None:
        self._adapters: dict[LLMProvider, LLMProviderAdapter] = {}

    def register_adapter(self, provider: LLMProvider, adapter: LLMProviderAdapter) -> None:
        """Register a provider adapter."""
        self._adapters[provider] = adapter
        logger.info("Registered LLM adapter for provider: %s", provider.value)

    def _get_adapter(self, provider: LLMProvider) -> LLMProviderAdapter:
        adapter = self._adapters.get(provider)
        if not adapter:
            raise ConfigurationError(f"No LLM adapter registered for provider: {provider.value}")
        return adapter

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Route and execute a generation request."""
        adapter = self._get_adapter(request.model_profile.provider)

        logger.debug(
            "Routing generate request to %s (model: %s)",
            request.model_profile.provider.value,
            request.model_profile.model_id,
        )

        try:
            # MVP: Direct passthrough to the adapter.
            # In the future, this is where retries, timeouts, and tracking go.
            return await adapter.generate(request)
        except Exception as e:
            if not isinstance(e, LLMError):
                e = LLMProviderError(
                    f"Unexpected error calling provider "
                    f"{request.model_profile.provider.value}: {e!s}",
                    provider=request.model_profile.provider.value,
                    model=request.model_profile.model_id,
                    cause=e,
                )
            raise e

    async def stream(self, request: LLMRequest) -> AsyncGenerator[LLMResponse, None]:  # type: ignore
        """Route and execute a streaming generation request."""
        adapter = self._get_adapter(request.model_profile.provider)

        logger.debug(
            "Routing stream request to %s (model: %s)",
            request.model_profile.provider.value,
            request.model_profile.model_id,
        )

        try:
            async for chunk in adapter.stream(request):
                yield chunk
        except Exception as e:
            if not isinstance(e, LLMError):
                raise LLMProviderError(
                    f"Unexpected error streaming from provider "
                    f"{request.model_profile.provider.value}: {e!s}",
                    provider=request.model_profile.provider.value,
                    model=request.model_profile.model_id,
                    cause=e,
                ) from e
            raise e
