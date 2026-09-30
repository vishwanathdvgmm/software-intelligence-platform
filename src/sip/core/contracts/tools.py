"""Tool and Agent Runtime contracts — Phase 7.

Defines the schema for tool definitions, execution, and bounded agent runs.

Security model:
- Every tool has an explicit ``ToolPermission`` set.
- The Tool Registry checks permissions before any execution.
- No arbitrary shell, SQL, or network access is permitted from LLM-directed
  tool calls — only allowlisted, schema-validated tools.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import Field

from sip.core.contracts.base import SIPBaseModel, new_uuid, utc_now

# ─── Enumerations ──────────────────────────────────────────────────────────


class ToolPermission(StrEnum):
    """Permissions a tool may require.

    An agent execution context declares the set of permissions it holds.
    A tool that requires a permission not held by the context is rejected.
    """

    KNOWLEDGE_READ = "knowledge_read"  # Read chunks/documents from the store
    KNOWLEDGE_WRITE = "knowledge_write"  # Trigger ingestion or modify sources
    EXPERT_READ = "expert_read"  # Read expert config
    EXPERT_WRITE = "expert_write"  # Modify expert config/status
    LLM_CALL = "llm_call"  # Make an LLM request
    NETWORK_READ = "network_read"  # HTTP GET to allowlisted URLs
    SYSTEM_READ = "system_read"  # Read system metrics/health


class ToolStatus(StrEnum):
    """Result status of a tool execution."""

    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    PERMISSION_DENIED = "permission_denied"
    INPUT_INVALID = "input_invalid"
    OUTPUT_INVALID = "output_invalid"


class AgentStatus(StrEnum):
    """Final status of an agent execution."""

    COMPLETED = "completed"
    STEP_LIMIT_EXCEEDED = "step_limit_exceeded"
    BUDGET_EXCEEDED = "budget_exceeded"
    ERROR = "error"


# ─── Tool contracts ─────────────────────────────────────────────────────────


class Tool(SIPBaseModel):
    """Definition of a registered tool.

    Tools are registered in the Tool Registry with an ID, schema, and
    permission set. The LLM sees the ``name``, ``description``, and
    ``input_schema`` only — never the implementation details.
    """

    id: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-z0-9_]+$")
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1)
    # JSON Schema for the input (as a dict, not a Pydantic model, to stay generic)
    input_schema: dict[str, object] = Field(default_factory=dict)
    # JSON Schema for the output
    output_schema: dict[str, object] = Field(default_factory=dict)
    # Required permissions for this tool
    required_permissions: frozenset[ToolPermission] = Field(default_factory=frozenset)
    is_active: bool = True


class ToolCall(SIPBaseModel):
    """A tool call requested by the LLM."""

    id: str = Field(default_factory=lambda: str(new_uuid()))
    tool_id: str
    # Raw input as provided by the LLM (pre-validation)
    raw_input: dict[str, object] = Field(default_factory=dict)


class ToolResult(SIPBaseModel):
    """Result of a single tool execution."""

    tool_call_id: str
    tool_id: str
    status: ToolStatus
    # Validated output (None on failure)
    output: dict[str, object] | None = None
    # Error message (None on success)
    error_message: str | None = None
    latency_ms: float | None = None
    executed_at: datetime = Field(default_factory=utc_now)


# ─── Agent execution ─────────────────────────────────────────────────────────


class AgentExecution(SIPBaseModel):
    """Context and result of a bounded agent run.

    The Agent Runtime enforces hard limits on steps and token budget to
    prevent runaway executions. These are contract-level limits — the runtime
    checks them after each step.
    """

    id: UUID = Field(default_factory=new_uuid)
    expert_id: UUID
    query_id: UUID | None = None
    # Permissions granted to this execution context
    granted_permissions: frozenset[ToolPermission] = Field(default_factory=frozenset)
    # Hard limits
    max_steps: int = Field(default=10, ge=1, le=50)
    max_tool_calls: int = Field(default=20, ge=1, le=100)
    token_budget: int = Field(default=8192, ge=1)
    # Execution result
    status: AgentStatus | None = None
    steps_taken: int = Field(default=0, ge=0)
    tool_calls_made: int = Field(default=0, ge=0)
    tokens_used: int = Field(default=0, ge=0)
    tool_results: tuple[ToolResult, ...] = Field(default_factory=tuple)
    started_at: datetime = Field(default_factory=utc_now)
    completed_at: datetime | None = None
    total_latency_ms: float | None = None
