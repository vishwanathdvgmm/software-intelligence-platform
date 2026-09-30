"""Tests for sip.core.errors — exception hierarchy."""

from __future__ import annotations

import pytest

from sip.core.errors import (
    AgentBudgetError,
    AgentError,
    AgentStepLimitError,
    AuthenticationError,
    AuthorizationError,
    CacheError,
    ChunkingError,
    ConfigurationError,
    ContextOptimizationError,
    DatabaseError,
    EmbeddingError,
    EvidenceError,
    ExpertError,
    ExpertNotFoundError,
    ExpertNotReadyError,
    ExpertStateError,
    FetchError,
    FusionError,
    IngestionError,
    LLMAuthenticationError,
    LLMError,
    LLMProviderError,
    LLMRateLimitError,
    LLMTimeoutError,
    ObjectStorageError,
    ParseError,
    RerankingError,
    RetrievalError,
    SIPError,
    StorageError,
    ToolError,
    ToolExecutionError,
    ToolInputError,
    ToolNotFoundError,
    ToolOutputError,
    ToolPermissionError,
    ToolTimeoutError,
    ValidationError,
    VectorStoreError,
)

class TestSIPError:
    def test_is_exception(self) -> None:
        err = SIPError("test message")
        assert isinstance(err, Exception)

    def test_message_stored(self) -> None:
        err = SIPError("something went wrong")
        assert err.message == "something went wrong"
        assert str(err) == "something went wrong"

    def test_cause_stored(self) -> None:
        cause = ValueError("root cause")
        err = SIPError("wrapper", cause=cause)
        assert err.cause is cause

    def test_str_with_cause(self) -> None:
        cause = ValueError("root cause")
        err = SIPError("wrapper", cause=cause)
        assert "wrapper" in str(err)
        assert "root cause" in str(err)

    def test_no_cause_by_default(self) -> None:
        err = SIPError("no cause")
        assert err.cause is None

class TestHierarchy:
    """Verify the inheritance hierarchy is correct."""

    @pytest.mark.parametrize(
        "exc_class,expected_bases",
        [
            (ConfigurationError, (SIPError,)),
            (ValidationError, (SIPError,)),
            (StorageError, (SIPError,)),
            (DatabaseError, (StorageError,)),
            (VectorStoreError, (StorageError,)),
            (CacheError, (StorageError,)),
            (ObjectStorageError, (StorageError,)),
            (RetrievalError, (SIPError,)),
            (EmbeddingError, (RetrievalError,)),
            (RerankingError, (RetrievalError,)),
            (FusionError, (RetrievalError,)),
            (ContextOptimizationError, (RetrievalError,)),
            (EvidenceError, (RetrievalError,)),
            (LLMError, (SIPError,)),
            (LLMProviderError, (LLMError,)),
            (LLMTimeoutError, (LLMError,)),
            (LLMRateLimitError, (LLMError,)),
            (LLMAuthenticationError, (LLMError,)),
            (ToolError, (SIPError,)),
            (ToolNotFoundError, (ToolError,)),
            (ToolPermissionError, (ToolError,)),
            (ToolInputError, (ToolError,)),
            (ToolOutputError, (ToolError,)),
            (ToolExecutionError, (ToolError,)),
            (ToolTimeoutError, (ToolError,)),
            (AgentError, (SIPError,)),
            (AgentStepLimitError, (AgentError,)),
            (AgentBudgetError, (AgentError,)),
            (ExpertError, (SIPError,)),
            (ExpertNotFoundError, (ExpertError,)),
            (ExpertStateError, (ExpertError,)),
            (ExpertNotReadyError, (ExpertError,)),
            (IngestionError, (SIPError,)),
            (FetchError, (IngestionError,)),
            (ParseError, (IngestionError,)),
            (ChunkingError, (IngestionError,)),
            (AuthorizationError, (SIPError,)),
            (AuthenticationError, (SIPError,)),
        ],
    )
    def test_base_class(
        self, exc_class: type[SIPError], expected_bases: tuple[type[Exception], ...]
    ) -> None:
        for base in expected_bases:
            assert issubclass(exc_class, base), (
                f"{exc_class.__name__} should be a subclass of {base.__name__}"
            )

    def test_all_sip_errors_are_sip_error(self) -> None:
        """Catch any SIP exception with a single except SIPError clause."""
        errors = [
            ConfigurationError("cfg"),
            ValidationError("val"),
            DatabaseError("db"),
            VectorStoreError("qdrant"),
            EmbeddingError("emb"),
            LLMProviderError("llm"),
            ToolNotFoundError("tool"),
            AgentStepLimitError("agent"),
            ExpertNotFoundError("expert"),
            FetchError("fetch"),
            AuthorizationError("auth"),
        ]
        for err in errors:
            assert isinstance(err, SIPError), f"{type(err).__name__} is not an instance of SIPError"

class TestSpecificErrors:
    def test_validation_error_field(self) -> None:
        err = ValidationError("bad value", field="query_text")
        assert err.field == "query_text"

    def test_validation_error_no_field(self) -> None:
        err = ValidationError("bad value")
        assert err.field is None

    def test_embedding_error_model(self) -> None:
        err = EmbeddingError("failed", model="all-MiniLM-L6-v2")
        assert err.model == "all-MiniLM-L6-v2"

    def test_reranking_error_model(self) -> None:
        err = RerankingError("failed", model="ms-marco-MiniLM")
        assert err.model == "ms-marco-MiniLM"

    def test_llm_error_provider_model(self) -> None:
        err = LLMError("timeout", provider="ollama", model="qwen2.5:7b")
        assert err.provider == "ollama"
        assert err.model == "qwen2.5:7b"

    def test_tool_error_tool_id(self) -> None:
        err = ToolNotFoundError("missing", tool_id="knowledge_search")
        assert err.tool_id == "knowledge_search"

    def test_expert_error_expert_id(self) -> None:
        err = ExpertNotFoundError("missing", expert_id="docker-expert")
        assert err.expert_id == "docker-expert"

    def test_ingestion_error_source_url(self) -> None:
        err = FetchError("404", source_url="https://docs.docker.com/")
        assert err.source_url == "https://docs.docker.com/"

class TestRaisable:
    """Verify all errors can be raised and caught correctly."""

    def test_raise_and_catch_sip_error(self) -> None:
        with pytest.raises(SIPError, match="oops"):
            raise SIPError("oops")

    def test_catch_subclass_as_base(self) -> None:
        with pytest.raises(StorageError):
            raise DatabaseError("connection refused")

    def test_catch_retrieval_as_sip(self) -> None:
        with pytest.raises(SIPError):
            raise EmbeddingError("model load failed")

    def test_raise_with_cause(self) -> None:
        original = OSError("disk full")
        with pytest.raises(StorageError) as exc_info:
            raise ObjectStorageError("write failed", cause=original)
        assert exc_info.value.cause is original
