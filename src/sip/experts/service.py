"""Expert Lifecycle Service — M5 implementation.

Manages Expert creation, configuration, state transitions, versioning,
readiness validation, and the Expert Registry.

This is the core business logic for Phase 6. It uses the repository
protocols from ``sip.core.protocols.repositories`` for persistence and
enforces the state machine defined in ``sip.core.contracts.experts``.
"""

from __future__ import annotations

import logging
from uuid import UUID

from sip.core.contracts.base import utc_now
from sip.core.contracts.experts import (
    EXPERT_VALID_TRANSITIONS,
    Expert,
    ExpertConfig,
    ExpertStatus,
    ExpertVersion,
)
from sip.core.errors import (
    ExpertNotFoundError,
    ExpertStateError,
    ValidationError,
)
from sip.core.protocols.repositories import ExpertRepository, ExpertVersionRepository

logger = logging.getLogger(__name__)


class ExpertLifecycleService:
    """Manages the full Expert lifecycle.

    Responsibilities:
      - Expert CRUD
      - State machine enforcement (DRAFT → … → ACTIVE)
      - Configuration versioning (ExpertVersion snapshots)
      - Readiness validation before activation
      - Expert registry queries
    """

    def __init__(
        self,
        expert_repo: ExpertRepository,
        version_repo: ExpertVersionRepository,
    ) -> None:
        self._expert_repo = expert_repo
        self._version_repo = version_repo

    # ─── Creation ──────────────────────────────────────────────────────────

    async def create_expert(
        self,
        name: str,
        slug: str,
        description: str = "",
        config: ExpertConfig | None = None,
    ) -> Expert:
        """Create a new Expert in DRAFT state.

        Args:
            name: Human-readable expert name (e.g. "Python Expert").
            slug: URL-friendly identifier (e.g. "python").
            description: Optional description of the expert's domain.
            config: Optional initial configuration.

        Returns:
            The newly created Expert entity.

        Raises:
            ValidationError: If an Expert with the same slug already exists.
        """
        existing = await self._expert_repo.get_by_slug(slug)
        if existing is not None:
            raise ValidationError(f"Expert with slug '{slug}' already exists (id={existing.id}).")

        expert = Expert(
            name=name,
            slug=slug,
            description=description,
            status=ExpertStatus.DRAFT,
            config=config or ExpertConfig(),
        )

        await self._expert_repo.save(expert)

        # Create initial version snapshot
        initial_version = ExpertVersion(
            expert_id=expert.id,
            version_number=1,
            config_snapshot=expert.config,
            change_reason="Initial creation",
        )
        await self._version_repo.save(initial_version)

        logger.info(
            "Created Expert '%s' (slug=%s, id=%s)",
            expert.name,
            expert.slug,
            expert.id,
        )
        return expert

    # ─── State Transitions ─────────────────────────────────────────────────

    async def transition(
        self,
        expert_id: UUID,
        target_status: ExpertStatus,
        reason: str = "",
    ) -> Expert:
        """Transition an Expert to a new lifecycle state.

        Enforces the state machine defined in ``EXPERT_VALID_TRANSITIONS``.
        On transition to ACTIVE, runs readiness validation.

        Args:
            expert_id: ID of the Expert to transition.
            target_status: Desired new state.
            reason: Optional reason for the transition.

        Returns:
            The updated Expert entity.

        Raises:
            ExpertNotFoundError: If no Expert with ``expert_id`` exists.
            InvalidStateTransitionError: If the transition is not allowed.
            ValidationError: If readiness checks fail (for ACTIVE transition).
        """
        expert = await self._get_expert_or_raise(expert_id)
        current = expert.status

        allowed = EXPERT_VALID_TRANSITIONS.get(current, frozenset())
        if target_status not in allowed:
            raise ExpertStateError(
                f"Cannot transition Expert '{expert.name}' "
                f"from {current.value} → {target_status.value}. "
                f"Allowed targets: {sorted(s.value for s in allowed)}"
            )

        # Gate: readiness validation before activation
        if target_status == ExpertStatus.ACTIVE:
            self._validate_readiness(expert)

        # Apply transition
        now = utc_now()
        updated = expert.model_copy(
            update={
                "status": target_status,
                "updated_at": now,
                **({"activated_at": now} if target_status == ExpertStatus.ACTIVE else {}),
            }
        )

        await self._expert_repo.save(updated)

        logger.info(
            "Expert '%s' transitioned %s → %s%s",
            expert.name,
            current.value,
            target_status.value,
            f" (reason: {reason})" if reason else "",
        )
        return updated

    # ─── Configuration Updates ─────────────────────────────────────────────

    async def update_config(
        self,
        expert_id: UUID,
        new_config: ExpertConfig,
        reason: str = "",
    ) -> Expert:
        """Update an Expert's configuration and create a new version snapshot.

        Can only be called when the Expert is in CONFIGURING or UPDATING state.

        Args:
            expert_id: ID of the Expert.
            new_config: The new configuration to apply.
            reason: Human-readable reason for the change.

        Returns:
            The updated Expert entity.

        Raises:
            ExpertNotFoundError: If no Expert with ``expert_id`` exists.
            ValidationError: If the Expert is not in a configurable state.
        """
        expert = await self._get_expert_or_raise(expert_id)

        configurable_states = {ExpertStatus.CONFIGURING, ExpertStatus.UPDATING, ExpertStatus.DRAFT}
        if expert.status not in configurable_states:
            raise ValidationError(
                f"Cannot update config for Expert '{expert.name}' "
                f"in state {expert.status.value}. "
                f"Must be in: {sorted(s.value for s in configurable_states)}"
            )

        new_version_number = expert.config_version + 1
        now = utc_now()

        updated = expert.model_copy(
            update={
                "config": new_config,
                "config_version": new_version_number,
                "updated_at": now,
            }
        )
        await self._expert_repo.save(updated)

        # Create immutable version snapshot
        version_snapshot = ExpertVersion(
            expert_id=expert.id,
            version_number=new_version_number,
            config_snapshot=new_config,
            change_reason=reason or "Configuration update",
        )
        await self._version_repo.save(version_snapshot)

        logger.info(
            "Expert '%s' config updated to v%d: %s",
            expert.name,
            new_version_number,
            reason or "(no reason given)",
        )
        return updated

    # ─── Registry Queries ──────────────────────────────────────────────────

    async def get_expert(self, expert_id: UUID) -> Expert:
        """Get an Expert by ID, raising if not found."""
        return await self._get_expert_or_raise(expert_id)

    async def get_expert_by_slug(self, slug: str) -> Expert | None:
        """Get an Expert by slug (returns None if not found)."""
        return await self._expert_repo.get_by_slug(slug)

    async def list_active_experts(self) -> list[Expert]:
        """List all Experts currently in ACTIVE state."""
        return await self._expert_repo.list_active()

    async def get_version_history(self, expert_id: UUID) -> list[ExpertVersion]:
        """Get the full configuration version history for an Expert."""
        await self._get_expert_or_raise(expert_id)  # ensure exists
        return await self._version_repo.list_by_expert(expert_id)

    # ─── Readiness Validation ──────────────────────────────────────────────

    def _validate_readiness(self, expert: Expert) -> None:
        """Validate that an Expert is ready for activation.

        Checks:
          1. Configuration has at least one software_id (knowledge scope).
          2. Expert is in READY state (caller already checked transition validity).
          3. System prompt template is defined (non-empty).

        Raises:
            ValidationError: With details of what failed.
        """
        errors: list[str] = []

        if not expert.config.software_ids:
            errors.append(
                "Expert must be associated with at least one Software (software_ids is empty)."
            )

        if not expert.config.generation.system_prompt_template:
            errors.append("Expert must have a system_prompt_template configured.")

        if errors:
            raise ValidationError(
                f"Expert '{expert.name}' failed readiness validation:\n"
                + "\n".join(f"  - {e}" for e in errors)
            )

    # ─── Internal ──────────────────────────────────────────────────────────

    async def _get_expert_or_raise(self, expert_id: UUID) -> Expert:
        """Fetch an Expert or raise ExpertNotFoundError."""
        expert = await self._expert_repo.get(expert_id)
        if expert is None:
            raise ExpertNotFoundError(f"Expert with id={expert_id} not found.")
        return expert
