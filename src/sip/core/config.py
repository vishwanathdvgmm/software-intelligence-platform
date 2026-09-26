"""SIP configuration — pydantic-settings backed, environment-driven.

All configurable defaults (LLM provider, embedding model, reranker model,
infrastructure endpoints) live here.  Nothing is hard-coded.

Usage
-----
    from sip.core.config import get_settings

    settings = get_settings()
    print(settings.llm.provider)

The singleton is cached after the first call.  In tests, call
``get_settings.cache_clear()`` after overriding environment variables to
force a fresh read.
"""

from __future__ import annotations

import functools
from enum import StrEnum

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# ─── Enums ─────────────────────────────────────────────────────────────────


class Environment(StrEnum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class LogFormat(StrEnum):
    CONSOLE = "console"
    JSON = "json"


class LogLevel(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class EmbeddingProvider(StrEnum):
    SENTENCE_TRANSFORMERS = "sentence_transformers"
    OPENAI = "openai"


class RerankerProvider(StrEnum):
    SENTENCE_TRANSFORMERS = "sentence_transformers"
    COHERE = "cohere"


class LLMProvider(StrEnum):
    OLLAMA = "ollama"
    OPENAI = "openai"
    GEMINI = "gemini"
    ANTHROPIC = "anthropic"


# ─── Sub-configs ───────────────────────────────────────────────────────────


class LoggingConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SIP_LOG_", extra="ignore")

    level: LogLevel = LogLevel.INFO
    format: LogFormat = LogFormat.CONSOLE


class PostgresConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SIP_POSTGRES_", extra="ignore")

    host: str = "localhost"
    port: int = 5432
    db: str = "sip"
    user: str = "sip"
    password: SecretStr = SecretStr("changeme")

    @property
    def dsn(self) -> str:
        """Async DSN for asyncpg / SQLAlchemy."""
        pw = self.password.get_secret_value()
        return f"postgresql+asyncpg://{self.user}:{pw}@{self.host}:{self.port}/{self.db}"


class QdrantConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SIP_QDRANT_", extra="ignore")

    host: str = "localhost"
    port: int = 6333
    api_key: SecretStr | None = None


class RedisConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SIP_REDIS_", extra="ignore")

    url: str = "redis://localhost:6379/0"


class EmbeddingConfig(BaseSettings):
    """Embedding model configuration.

    These are configurable defaults — they are not architectural lock-ins.
    Changing the model here (plus re-indexing) is the only required change.
    The ``model_version`` field must be bumped whenever the model changes so
    that retrieval reproducibility records remain accurate.
    """

    model_config = SettingsConfigDict(env_prefix="SIP_EMBEDDING_", extra="ignore")

    provider: EmbeddingProvider = EmbeddingProvider.SENTENCE_TRANSFORMERS
    model: str = "sentence-transformers/all-MiniLM-L6-v2"
    dimension: int = 384
    # Increment this when the model changes — all existing vectors are invalid.
    model_version: str = "1"

    @field_validator("dimension")
    @classmethod
    def dimension_must_be_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("embedding dimension must be a positive integer")
        return v


class RerankerConfig(BaseSettings):
    """Cross-encoder / reranker configuration.

    Configurable default, not a lock-in.  Swap by changing env vars.
    """

    model_config = SettingsConfigDict(env_prefix="SIP_RERANKER_", extra="ignore")

    provider: RerankerProvider = RerankerProvider.SENTENCE_TRANSFORMERS
    model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    model_version: str = "1"


class LLMConfig(BaseSettings):
    """LLM provider and model configuration.

    Configurable default, not a lock-in.  Swap provider/model via env vars.
    """

    model_config = SettingsConfigDict(env_prefix="SIP_LLM_", extra="ignore")

    provider: LLMProvider = LLMProvider.OLLAMA
    model: str = "qwen2.5:7b"
    # Required when provider = ollama
    base_url: str = "http://localhost:11434"
    # API keys — injected from environment, never stored in source
    openai_api_key: SecretStr | None = Field(
        default=None, alias="SIP_OPENAI_API_KEY", validation_alias="SIP_OPENAI_API_KEY"
    )
    gemini_api_key: SecretStr | None = Field(
        default=None, alias="SIP_GEMINI_API_KEY", validation_alias="SIP_GEMINI_API_KEY"
    )
    anthropic_api_key: SecretStr | None = Field(
        default=None,
        alias="SIP_ANTHROPIC_API_KEY",
        validation_alias="SIP_ANTHROPIC_API_KEY",
    )

    model_config = SettingsConfigDict(
        env_prefix="SIP_LLM_",
        extra="ignore",
        populate_by_name=True,
    )


# ─── Root settings ─────────────────────────────────────────────────────────


class Settings(BaseSettings):
    """Root SIP settings object.

    Reads from environment variables and, if present, a ``.env`` file
    in the working directory.
    """

    model_config = SettingsConfigDict(
        env_prefix="SIP_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    env: Environment = Environment.DEVELOPMENT

    # Sub-configs — each reads its own env-prefix independently.
    # default_factory ensures a fresh instance is created per Settings object.
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    postgres: PostgresConfig = Field(default_factory=PostgresConfig)
    qdrant: QdrantConfig = Field(default_factory=QdrantConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    embedding: EmbeddingConfig = Field(default_factory=EmbeddingConfig)
    reranker: RerankerConfig = Field(default_factory=RerankerConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)

    @property
    def is_development(self) -> bool:
        return self.env == Environment.DEVELOPMENT

    @property
    def is_testing(self) -> bool:
        return self.env == Environment.TESTING

    @property
    def is_production(self) -> bool:
        return self.env == Environment.PRODUCTION


# ─── Singleton accessor ────────────────────────────────────────────────────


@functools.lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached Settings singleton.

    Call ``get_settings.cache_clear()`` in tests to reset after
    env-var overrides.
    """
    return Settings()
