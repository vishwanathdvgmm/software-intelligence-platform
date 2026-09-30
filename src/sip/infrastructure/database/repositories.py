"""PostgreSQL implementations of the repository protocols."""

from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sip.core.contracts.experts import Expert, ExpertConfig, ExpertStatus, ExpertVersion
from sip.infrastructure.database.models import ExpertModel, ExpertVersionModel


class PostgresExpertRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, expert_id: UUID) -> Expert | None:
        stmt = select(ExpertModel).where(ExpertModel.id == expert_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_entity(model)

    async def save(self, expert: Expert) -> None:
        stmt = select(ExpertModel).where(ExpertModel.id == expert.id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if not model:
            model = ExpertModel(
                id=expert.id,
                name=expert.name,
                slug=expert.slug,
                description=expert.description,
                status=expert.status.value,
                config=expert.config.model_dump(mode="json"),
                config_version=expert.config_version,
                created_at=expert.created_at,
                updated_at=expert.updated_at,
                activated_at=expert.activated_at,
            )
            self._session.add(model)
        else:
            model.name = expert.name
            model.slug = expert.slug
            model.description = expert.description
            model.status = expert.status.value
            model.config = expert.config.model_dump(mode="json")
            model.config_version = expert.config_version
            model.updated_at = expert.updated_at
            model.activated_at = expert.activated_at
        
        await self._session.flush()

    async def get_by_slug(self, slug: str) -> Expert | None:
        stmt = select(ExpertModel).where(ExpertModel.slug == slug)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_entity(model)

    async def list_active(self) -> list[Expert]:
        stmt = select(ExpertModel).where(ExpertModel.status == ExpertStatus.ACTIVE.value)
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def list_all(self) -> list[Expert]:
        """List all experts regardless of state (for UI admin panel)."""
        stmt = select(ExpertModel).order_by(ExpertModel.created_at.desc())
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    def _to_entity(self, model: ExpertModel) -> Expert:
        return Expert(
            id=model.id,
            name=model.name,
            slug=model.slug,
            description=model.description,
            status=ExpertStatus(model.status),
            config=ExpertConfig.model_validate(model.config),
            config_version=model.config_version,
            created_at=model.created_at,
            updated_at=model.updated_at,
            activated_at=model.activated_at,
        )

class PostgresExpertVersionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, version: ExpertVersion) -> None:
        model = ExpertVersionModel(
            id=version.id,
            expert_id=version.expert_id,
            version_number=version.version_number,
            config_snapshot=version.config_snapshot.model_dump(mode="json"),
            change_reason=version.change_reason,
            created_at=version.created_at,
            created_by=version.created_by,
        )
        self._session.add(model)
        await self._session.flush()

    async def get_latest(self, expert_id: UUID) -> ExpertVersion | None:
        stmt = (
            select(ExpertVersionModel)
            .where(ExpertVersionModel.expert_id == expert_id)
            .order_by(ExpertVersionModel.version_number.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_entity(model)

    async def list_by_expert(self, expert_id: UUID) -> list[ExpertVersion]:
        stmt = (
            select(ExpertVersionModel)
            .where(ExpertVersionModel.expert_id == expert_id)
            .order_by(ExpertVersionModel.version_number.desc())
        )
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    def _to_entity(self, model: ExpertVersionModel) -> ExpertVersion:
        return ExpertVersion(
            id=model.id,
            expert_id=model.expert_id,
            version_number=model.version_number,
            config_snapshot=ExpertConfig.model_validate(model.config_snapshot),
            change_reason=model.change_reason,
            created_at=model.created_at,
            created_by=model.created_by,
        )
