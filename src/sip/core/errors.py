"""SIP exception hierarchy.

All SIP exceptions derive from SIPError so callers can distinguish
SIP-domain failures from general Python exceptions.

Design rules:
- Every exception carries a human-readable ``message``.
- Subsystem-specific exceptions extend the relevant base (e.g.,
  RetrievalError for anything inside the RAG retrieval pipeline).
- Use specific exceptions at raise sites; catch broad bases only at
  subsystem or API boundaries.
"""

from __future__ import annotations

# ─── Root ──────────────────────────────────────────────────────────────────

class SIPError(Exception):
    """Base class for all SIP domain exceptions."""

    def __init__(self, message: str, *, cause: BaseException | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.cause = cause

    def __str__(self) -> str:
        if self.cause:
            return f"{self.message} (caused by: {self.cause!r})"
        return self.message

# ─── Configuration ─────────────────────────────────────────────────────────

class ConfigurationError(SIPError):
    """Invalid or missing configuration."""

# ─── Validation ────────────────────────────────────────────────────────────

class ValidationError(SIPError):
    """Input failed schema or semantic validation."""

    def __init__(
        self,
        message: str,
        *,
        field: str | None = None,
        cause: BaseException | None = None,
    ) -> None:
        super().__init__(message, cause=cause)
        self.field = field

# ─── Storage ───────────────────────────────────────────────────────────────

class StorageError(SIPError):
    """Base for all persistence / storage failures."""

class DatabaseError(StorageError):
    """PostgreSQL or relational database failure."""

class VectorStoreError(StorageError):
    """Qdrant or vector store failure."""

class CacheError(StorageError):
    """Redis or cache layer failure."""

class ObjectStorageError(StorageError):
    """Object / file storage failure."""

# ─── Retrieval ─────────────────────────────────────────────────────────────

class RetrievalError(SIPError):
    """Base for all retrieval pipeline failures."""

class EmbeddingError(RetrievalError):
    """Embedding generation failed."""

    def __init__(
        self,
        message: str,
        *,
        model: str | None = None,
        cause: BaseException | None = None,
    ) -> None:
        super().__init__(message, cause=cause)
        self.model = model

class RerankingError(RetrievalError):
    """Cross-encoder reranking failed."""

    def __init__(
        self,
        message: str,
        *,
        model: str | None = None,
        cause: BaseException | None = None,
    ) -> None:
        super().__init__(message, cause=cause)
        self.model = model

class FusionError(RetrievalError):
    """Result fusion (RRF or other) failed."""

class ContextOptimizationError(RetrievalError):
    """Context optimization or compression failed."""

class EvidenceError(RetrievalError):
    """Evidence evaluation or gating failed."""

# ─── LLM / Generation ──────────────────────────────────────────────────────

class LLMError(SIPError):
    """Base for all LLM Gateway failures."""

    def __init__(
        self,
        message: str,
        *,
        provider: str | None = None,
        model: str | None = None,
        cause: BaseException | None = None,
    ) -> None:
        super().__init__(message, cause=cause)
        self.provider = provider
        self.model = model

class LLMProviderError(LLMError):
    """The LLM provider returned an error response."""

class LLMTimeoutError(LLMError):
    """LLM request exceeded the configured timeout."""

class LLMRateLimitError(LLMError):
    """LLM provider rate limit was hit."""

class LLMAuthenticationError(LLMError):
    """LLM provider authentication failed (bad API key, etc.)."""

# ─── Tools ─────────────────────────────────────────────────────────────────

class ToolError(SIPError):
    """Base for all tool execution failures."""

    def __init__(
        self,
        message: str,
        *,
        tool_id: str | None = None,
        cause: BaseException | None = None,
    ) -> None:
        super().__init__(message, cause=cause)
        self.tool_id = tool_id

class ToolNotFoundError(ToolError):
    """The requested tool is not registered."""

class ToolPermissionError(ToolError):
    """The caller does not have permission to execute this tool."""

class ToolInputError(ToolError):
    """Tool input failed schema validation."""

class ToolOutputError(ToolError):
    """Tool output failed schema validation."""

class ToolExecutionError(ToolError):
    """Tool execution raised an unexpected error."""

class ToolTimeoutError(ToolError):
    """Tool execution exceeded its timeout budget."""

# ─── Agents ────────────────────────────────────────────────────────────────

class AgentError(SIPError):
    """Base for Agent Runtime failures."""

class AgentStepLimitError(AgentError):
    """Agent exceeded the maximum number of reasoning steps."""

class AgentBudgetError(AgentError):
    """Agent exceeded its execution token/cost budget."""

# ─── Experts ───────────────────────────────────────────────────────────────

class ExpertError(SIPError):
    """Base for Expert system failures."""

    def __init__(
        self,
        message: str,
        *,
        expert_id: str | None = None,
        cause: BaseException | None = None,
    ) -> None:
        super().__init__(message, cause=cause)
        self.expert_id = expert_id

class ExpertNotFoundError(ExpertError):
    """The requested Expert does not exist."""

class ExpertStateError(ExpertError):
    """An invalid lifecycle state transition was attempted."""

class ExpertNotReadyError(ExpertError):
    """The Expert is not in a state that can serve queries."""

# ─── Ingestion ─────────────────────────────────────────────────────────────

class IngestionError(SIPError):
    """Base for knowledge ingestion failures."""

    def __init__(
        self,
        message: str,
        *,
        source_url: str | None = None,
        cause: BaseException | None = None,
    ) -> None:
        super().__init__(message, cause=cause)
        self.source_url = source_url

class FetchError(IngestionError):
    """HTTP fetch of a source URL failed."""

class ParseError(IngestionError):
    """Content parsing or extraction failed."""

class ChunkingError(IngestionError):
    """Document chunking failed."""

# ─── Authorization ─────────────────────────────────────────────────────────

class AuthorizationError(SIPError):
    """The caller is not permitted to perform this operation."""

class AuthenticationError(SIPError):
    """The caller could not be authenticated."""
