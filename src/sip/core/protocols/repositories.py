"""Storage-agnostic repository protocols — M3/M5 requirements.

These protocols abstract the PostgreSQL database for the core entities.
"""

from typing import Protocol
from uuid import UUID

from sip.core.contracts import Expert, ExpertVersion


class ExpertRepository(Protocol):
    """Protocol for managing Expert entities."""

    async def get(self, expert_id: UUID) -> Expert | None:
        """Get an Expert by ID."""
        ...

    async def save(self, expert: Expert) -> None:
        """Save a new or updated Expert."""
        ...

    async def get_by_slug(self, slug: str) -> Expert | None:
        """Get an Expert by its URL-friendly slug."""
        ...

    async def list_active(self) -> list[Expert]:
        """List all Experts in the ACTIVE state."""
        ...


class ExpertVersionRepository(Protocol):
    """Protocol for managing Expert config snapshots."""

    async def save(self, version: ExpertVersion) -> None:
        """Save a new ExpertVersion snapshot."""
        ...

    async def get_latest(self, expert_id: UUID) -> ExpertVersion | None:
        """Get the most recent ExpertVersion for an Expert."""
        ...

    async def list_by_expert(self, expert_id: UUID) -> list[ExpertVersion]:
        """List all versions for an Expert, ordered by version_number descending."""
        ...
