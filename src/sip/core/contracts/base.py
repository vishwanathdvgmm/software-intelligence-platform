"""SIP base model and shared types.

All SIP contracts extend ``SIPBaseModel`` which enforces:
- Immutability (frozen=True) — contracts are value objects, not mutable entities.
- Strict validation (validate_assignment=True).
- JSON-safe serialization via model_dump(mode="json").
- Consistent UUID-based IDs.

Shared enumerations that span multiple contract domains are also defined here.
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

# ─── Base model ────────────────────────────────────────────────────────────


class SIPBaseModel(BaseModel):
    """Base for all SIP data contracts.

    Frozen so contracts behave as immutable value objects — safe to share
    across async tasks without defensive copying.
    """

    model_config = ConfigDict(
        frozen=True,
        validate_assignment=True,
        populate_by_name=True,
        arbitrary_types_allowed=False,
        str_strip_whitespace=True,
        use_enum_values=False,
    )


# ─── Common field factories ─────────────────────────────────────────────────


def new_uuid() -> UUID:
    """Generate a new random UUID v4."""
    return uuid4()


def utc_now() -> datetime:
    """Return the current UTC time (timezone-aware)."""
    return datetime.now(UTC)


# ─── Common field types ─────────────────────────────────────────────────────

# Re-export for use in contract modules without re-importing uuid/datetime.
__all__ = [
    "UUID",
    "Field",
    "SIPBaseModel",
    "datetime",
    "new_uuid",
    "utc_now",
]
