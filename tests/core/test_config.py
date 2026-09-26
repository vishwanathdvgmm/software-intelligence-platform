"""Tests for sip.core.config — settings and environment handling."""

from __future__ import annotations

import pytest

from sip.core.config import (
    EmbeddingProvider,
    Environment,
    LLMProvider,
    LogFormat,
    LogLevel,
    RerankerProvider,
    get_settings,
)


class TestDefaultSettings:
    def test_default_env_is_development_in_tests(self) -> None:
        # conftest.py sets SIP_ENV=testing
        settings = get_settings()
        assert settings.env == Environment.TESTING

    def test_is_testing_property(self) -> None:
        settings = get_settings()
        assert settings.is_testing is True
        assert settings.is_production is False
        assert settings.is_development is False

    def test_default_embedding_provider(self) -> None:
        settings = get_settings()
        assert settings.embedding.provider == EmbeddingProvider.SENTENCE_TRANSFORMERS

    def test_default_embedding_model(self) -> None:
        settings = get_settings()
        assert "MiniLM" in settings.embedding.model

    def test_default_embedding_dimension(self) -> None:
        settings = get_settings()
        assert settings.embedding.dimension == 384

    def test_default_reranker_provider(self) -> None:
        settings = get_settings()
        assert settings.reranker.provider == RerankerProvider.SENTENCE_TRANSFORMERS

    def test_default_llm_provider(self) -> None:
        settings = get_settings()
        assert settings.llm.provider == LLMProvider.OLLAMA

    def test_default_log_level(self) -> None:
        # conftest.py sets SIP_LOG_LEVEL=DEBUG
        settings = get_settings()
        assert settings.logging.level == LogLevel.DEBUG

    def test_default_log_format(self) -> None:
        # conftest.py sets SIP_LOG_FORMAT=console
        settings = get_settings()
        assert settings.logging.format == LogFormat.CONSOLE


class TestEnvVarOverrides:
    def test_override_environment(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("SIP_ENV", "production")
        get_settings.cache_clear()
        settings = get_settings()
        assert settings.env == Environment.PRODUCTION
        assert settings.is_production is True

    def test_override_embedding_model(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("SIP_EMBEDDING_MODEL", "openai/text-embedding-3-small")
        monkeypatch.setenv("SIP_EMBEDDING_PROVIDER", "openai")
        monkeypatch.setenv("SIP_EMBEDDING_DIMENSION", "1536")
        get_settings.cache_clear()
        settings = get_settings()
        assert settings.embedding.model == "openai/text-embedding-3-small"
        assert settings.embedding.provider == EmbeddingProvider.OPENAI
        assert settings.embedding.dimension == 1536

    def test_override_llm_provider(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("SIP_LLM_PROVIDER", "openai")
        monkeypatch.setenv("SIP_LLM_MODEL", "gpt-4o")
        get_settings.cache_clear()
        settings = get_settings()
        assert settings.llm.provider == LLMProvider.OPENAI
        assert settings.llm.model == "gpt-4o"

    def test_override_reranker(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("SIP_RERANKER_PROVIDER", "cohere")
        monkeypatch.setenv("SIP_RERANKER_MODEL", "rerank-multilingual-v3.0")
        get_settings.cache_clear()
        settings = get_settings()
        assert settings.reranker.provider == RerankerProvider.COHERE
        assert settings.reranker.model == "rerank-multilingual-v3.0"


class TestPostgresDSN:
    def test_dsn_format(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("SIP_POSTGRES_HOST", "db-host")
        monkeypatch.setenv("SIP_POSTGRES_PORT", "5432")
        monkeypatch.setenv("SIP_POSTGRES_DB", "mydb")
        monkeypatch.setenv("SIP_POSTGRES_USER", "myuser")
        monkeypatch.setenv("SIP_POSTGRES_PASSWORD", "mypassword")
        get_settings.cache_clear()
        settings = get_settings()
        dsn = settings.postgres.dsn
        assert dsn.startswith("postgresql+asyncpg://")
        assert "db-host" in dsn
        assert "mydb" in dsn
        assert "myuser" in dsn
        # Password should appear in DSN (it's used to connect)
        assert "mypassword" in dsn

    def test_password_is_secret(self) -> None:
        settings = get_settings()
        # SecretStr should not expose password in repr
        repr_str = repr(settings.postgres.password)
        assert "changeme" not in repr_str
        assert "**" in repr_str


class TestEmbeddingDimensionValidation:
    def test_invalid_dimension_zero(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("SIP_EMBEDDING_DIMENSION", "0")
        get_settings.cache_clear()
        with pytest.raises(ValueError, match="positive"):
            get_settings()

    def test_invalid_dimension_negative(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("SIP_EMBEDDING_DIMENSION", "-1")
        get_settings.cache_clear()
        with pytest.raises(ValueError, match="positive"):
            get_settings()


class TestModelVersionTracking:
    """Verify model version fields exist for retrieval reproducibility."""

    def test_embedding_has_model_version(self) -> None:
        settings = get_settings()
        assert settings.embedding.model_version
        assert isinstance(settings.embedding.model_version, str)

    def test_reranker_has_model_version(self) -> None:
        settings = get_settings()
        assert settings.reranker.model_version
        assert isinstance(settings.reranker.model_version, str)


class TestSettingsSingleton:
    def test_get_settings_returns_same_instance(self) -> None:
        s1 = get_settings()
        s2 = get_settings()
        assert s1 is s2

    def test_cache_clear_returns_new_instance(self) -> None:
        s1 = get_settings()
        get_settings.cache_clear()
        s2 = get_settings()
        # Different instances after cache clear
        assert s1 is not s2
