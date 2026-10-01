"""Tests for M1 Core API Contracts."""

import pytest
from pydantic import ValidationError

from sip.core.contracts.api import (
    APIError,
    APIErrorDetail,
    HealthStatus,
    PlatformAPIResponse,
    StreamingEvent,
)

def test_health_status() -> None:
    health = HealthStatus(status="ok", version="1.0.0", components={"db": "up"})
    assert health.status == "ok"
    assert health.components["db"] == "up"

def test_api_error() -> None:
    error_detail = APIErrorDetail(code="NOT_FOUND", message="Resource missing", details={"id": 1})
    error = APIError(error=error_detail)
    assert error.error.code == "NOT_FOUND"

def test_platform_api_response() -> None:
    res = PlatformAPIResponse[str](data="test data", meta={"key": "value"})
    assert res.data == "test data"
    assert res.meta["key"] == "value"
    assert res.trace is None

def test_streaming_event() -> None:
    event = StreamingEvent(event_type="chunk", data={"text": "hello"}, seq=1)
    assert event.event_type == "chunk"
    assert event.seq == 1
    
    with pytest.raises(ValidationError):
        # missing seq
        StreamingEvent(event_type="chunk", data={})  # type: ignore
