"""SIP Core Contracts — M1 public API.

All data contracts for the SIP system are exported from this module.
Import from here rather than from individual sub-modules:

    from sip.core.contracts import Chunk, Query, Expert, LLMRequest

Sub-modules:
    base        — SIPBaseModel, UUID helpers
    knowledge   — Software, SoftwareVersion, Source, Document, Chunk, KnowledgeRecord
    rag         — Query pipeline contracts + RetrievalVersionSnapshot
    experts     — Expert, ExpertConfig, ExpertVersion, ExpertStatus
    llm         — LLMRequest, LLMResponse, ModelProfile, TokenUsage
    tools       — Tool, ToolResult, ToolPermission, AgentExecution
    output      — Citation, ExecutionTrace, EvaluationResult
"""

from sip.core.contracts.base import SIPBaseModel, new_uuid, utc_now
from sip.core.contracts.experts import (
    EXPERT_VALID_TRANSITIONS,
    EvidenceConfig,
    Expert,
    ExpertConfig,
    ExpertStatus,
    ExpertVersion,
    GenerationConfig,
    RetrievalConfig,
    VersionPolicy,
)
from sip.core.contracts.knowledge import (
    AuthorityLevel,
    Chunk,
    ChunkType,
    Document,
    DocumentType,
    DocumentVersion,
    IngestionStatus,
    KnowledgeRecord,
    Section,
    Software,
    SoftwareVersion,
    Source,
    SourceType,
)
from sip.core.contracts.llm import (
    FinishReason,
    LLMProvider,
    LLMRequest,
    LLMResponse,
    Message,
    MessageRole,
    ModelProfile,
    TokenUsage,
)
from sip.core.contracts.output import (
    Citation,
    EvaluationResult,
    EvaluationSystem,
    ExecutionTrace,
    MetricValue,
    RetrievalTraceEntry,
)
from sip.core.contracts.rag import (
    Context,
    Evidence,
    EvidenceSufficiency,
    EvidenceSufficiencyAssessment,
    Query,
    QueryAnalysis,
    QueryComplexity,
    QueryType,
    RetrievalCandidate,
    RetrievalPlan,
    RetrievalResult,
    RetrievalStrategy,
    RetrievalVersionSnapshot,
)
from sip.core.contracts.tools import (
    AgentExecution,
    AgentStatus,
    Tool,
    ToolCall,
    ToolPermission,
    ToolResult,
    ToolStatus,
)

__all__ = [
    "EXPERT_VALID_TRANSITIONS",
    "AgentExecution",
    "AgentStatus",
    "AuthorityLevel",
    "Chunk",
    "ChunkType",
    # output
    "Citation",
    "Context",
    "Document",
    "DocumentType",
    "DocumentVersion",
    "EvaluationResult",
    "EvaluationSystem",
    "Evidence",
    "EvidenceConfig",
    "EvidenceSufficiency",
    "EvidenceSufficiencyAssessment",
    "ExecutionTrace",
    "Expert",
    "ExpertConfig",
    # experts
    "ExpertStatus",
    "ExpertVersion",
    "FinishReason",
    "GenerationConfig",
    "IngestionStatus",
    "KnowledgeRecord",
    "LLMProvider",
    "LLMRequest",
    "LLMResponse",
    "Message",
    # llm
    "MessageRole",
    "MetricValue",
    "ModelProfile",
    # rag
    "Query",
    "QueryAnalysis",
    "QueryComplexity",
    "QueryType",
    "RetrievalCandidate",
    "RetrievalConfig",
    "RetrievalPlan",
    "RetrievalResult",
    "RetrievalStrategy",
    "RetrievalTraceEntry",
    "RetrievalVersionSnapshot",
    # base
    "SIPBaseModel",
    "Section",
    # knowledge
    "Software",
    "SoftwareVersion",
    "Source",
    "SourceType",
    "TokenUsage",
    "Tool",
    "ToolCall",
    # tools
    "ToolPermission",
    "ToolResult",
    "ToolStatus",
    "VersionPolicy",
    "new_uuid",
    "utc_now",
]
