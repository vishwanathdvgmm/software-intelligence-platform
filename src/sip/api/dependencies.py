"""FastAPI dependency providers."""

from typing import AsyncGenerator, cast

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from sip.core.container import ApplicationContainer
from sip.core.engine.orchestrator import AdaptiveRAGEngine
from sip.infrastructure.database.repositories import PostgresExpertRepository

def get_container(request: Request) -> ApplicationContainer:
    """Get the application container from request state."""
    container = getattr(request.app.state, "container", None)
    if container is None:
        raise RuntimeError("Application container is not initialized")
    return cast(ApplicationContainer, container)

async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """Yield a database session from the container."""
    container = get_container(request)
    async with container.get_db_session() as session:
        yield session

def get_rag_engine(request: Request) -> AdaptiveRAGEngine:
    """Get the RAG engine from the container."""
    container = get_container(request)
    if container.rag_engine is None:
        raise RuntimeError("RAG engine is not initialized")
    return container.rag_engine
