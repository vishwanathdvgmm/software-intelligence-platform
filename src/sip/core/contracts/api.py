"""API contracts.

Defines the core data structures for HTTP/API boundaries, including requests,
responses, error models, and health status, preserving framework independence.
"""

from typing import Dict, Any, Generic, TypeVar, List
from pydantic import Field, BaseModel

from sip.core.contracts.base import SIPBaseModel
from sip.core.contracts.output import ExecutionTrace

T = TypeVar("T")

class HealthStatus(SIPBaseModel):
    """Canonical representation of platform health."""
    status: str
    version: str
    components: Dict[str, str] = Field(default_factory=dict)

class APIErrorDetail(SIPBaseModel):
    """Detailed error information."""
    code: str
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)

class APIError(SIPBaseModel):
    """Canonical API Error structure."""
    error: APIErrorDetail

class PlatformAPIResponse(SIPBaseModel, Generic[T]):
    """Standard wrapper for API responses."""
    data: T
    trace: ExecutionTrace | None = None
    meta: Dict[str, Any] = Field(default_factory=dict)

class StreamingEvent(SIPBaseModel):
    """A single event emitted during a streaming API response."""
    event_type: str
    data: Dict[str, Any]
    seq: int
