"""LLM Gateway and Provider protocols — M6 requirements.

These protocols define the boundary between the SIP runtime and external
LLM providers (OpenAI, Gemini, Ollama, etc.).
"""

from collections.abc import AsyncGenerator
from typing import Protocol

from sip.core.contracts.llm import LLMRequest, LLMResponse


class LLMProviderAdapter(Protocol):
    """Protocol for a specific LLM provider implementation.

    Adapters translate SIP's agnostic LLMRequest into provider-specific API
    calls, and translate the response back into LLMResponse.
    """

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate a complete response from the provider."""
        ...

    def stream(self, request: LLMRequest) -> AsyncGenerator[LLMResponse, None]:
        """Stream a response from the provider as a sequence of partial LLMResponses."""
        ...


class LLMGateway(Protocol):
    """Protocol for the central LLM Gateway.

    The application interacts only with the Gateway, not directly with Adapters.
    The Gateway handles routing, retries, timeout enforcement, and cost tracking.
    """

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Route and execute a generation request."""
        ...

    def stream(self, request: LLMRequest) -> AsyncGenerator[LLMResponse, None]:
        """Route and execute a streaming generation request."""
        ...
