"""LLM Gateway contracts — Phase 7.

Provider-agnostic contracts for all LLM interactions.
The gateway accepts ``LLMRequest`` and returns ``LLMResponse`` regardless
of whether the backend is Ollama, OpenAI, Gemini, or Anthropic.

No provider-specific types appear here — provider adapters translate
between these contracts and their native API formats.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import Field

from sip.core.contracts.base import SIPBaseModel, new_uuid, utc_now

# ─── Enumerations ──────────────────────────────────────────────────────────


class MessageRole(StrEnum):
    """Role of a message in a conversation."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class LLMProvider(StrEnum):
    """Supported LLM providers."""

    OLLAMA = "ollama"
    OPENAI = "openai"
    GEMINI = "gemini"
    ANTHROPIC = "anthropic"


class FinishReason(StrEnum):
    """Why the LLM stopped generating."""

    STOP = "stop"             # Natural end of response
    LENGTH = "length"         # Hit max_tokens limit
    TOOL_CALL = "tool_call"   # Model wants to call a tool
    CONTENT_FILTER = "content_filter"  # Blocked by safety filter
    ERROR = "error"           # Provider error


# ─── Message and request/response ─────────────────────────────────────────


class Message(SIPBaseModel):
    """A single message in a conversation."""

    role: MessageRole
    content: str
    # Tool call ID (populated when role=TOOL, referencing the tool call)
    tool_call_id: str | None = None


class TokenUsage(SIPBaseModel):
    """Token consumption for a single LLM call."""

    input_tokens: int = Field(..., ge=0)
    output_tokens: int = Field(..., ge=0)
    total_tokens: int = Field(..., ge=0)
    # Cached input tokens (OpenAI prompt caching, if supported)
    cached_input_tokens: int = Field(default=0, ge=0)


class ModelProfile(SIPBaseModel):
    """Configuration profile for a specific model.

    Configurable defaults — not lock-ins. Swap via config or ExpertConfig.
    """

    provider: LLMProvider
    model_id: str = Field(..., min_length=1)
    # Human-readable display name
    display_name: str = Field(default="")
    # Maximum context window in tokens
    context_window: int = Field(..., ge=1)
    # Maximum output tokens
    max_output_tokens: int = Field(default=4096, ge=1)
    # Whether the model supports tool/function calling
    supports_tool_calls: bool = False
    # Whether the model supports streaming
    supports_streaming: bool = True
    # Provider base URL (required for Ollama, optional for cloud providers)
    base_url: str | None = None


class LLMRequest(SIPBaseModel):
    """Provider-agnostic LLM generation request."""

    id: UUID = Field(default_factory=new_uuid)
    model_profile: ModelProfile
    messages: tuple[Message, ...]
    temperature: float = Field(default=0.1, ge=0.0, le=2.0)
    max_output_tokens: int = Field(default=2048, ge=1)
    stream: bool = False
    # Tool schemas available to the model (empty = no tool calling)
    available_tool_ids: tuple[str, ...] = Field(default_factory=tuple)
    # Correlation IDs for tracing
    query_id: UUID | None = None
    expert_id: UUID | None = None
    created_at: datetime = Field(default_factory=utc_now)


class LLMResponse(SIPBaseModel):
    """Provider-agnostic LLM generation response."""

    request_id: UUID
    content: str
    finish_reason: FinishReason
    usage: TokenUsage
    # Raw model identifier as returned by the provider
    model_used: str
    provider: LLMProvider
    latency_ms: float | None = None
    created_at: datetime = Field(default_factory=utc_now)
