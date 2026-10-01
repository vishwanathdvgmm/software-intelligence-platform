"""Application composition root.

Provides deterministic startup, dependency injection, and shutdown.
"""
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from qdrant_client import AsyncQdrantClient
import structlog
import os
from uuid import UUID, uuid4

from sip.core.config import Settings
from sip.core.contracts.rag import RetrievalVersionSnapshot, RetrievalStrategy
from sip.core.engine.orchestrator import AdaptiveRAGEngine
from sip.infrastructure.retrieval.qdrant import QdrantSemanticRetriever
from sip.core.protocols.retrieval import LexicalRetriever
from sip.core.contracts.knowledge import KnowledgeRecord

logger = structlog.get_logger(__name__)

class MockLexicalRetriever(LexicalRetriever):
    async def search(self, query_text: str, expert_id: UUID, version_filter: dict[str, list[str] | str], top_k: int) -> list[tuple[KnowledgeRecord, float]]:
        return []

class ApplicationContainer:
    """Composition root for the SIP Core application."""
    
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.pg_engine: AsyncEngine | None = None
        self.async_session_maker: async_sessionmaker[AsyncSession] | None = None
        self.qdrant_client: AsyncQdrantClient | None = None
        
        # Application services
        self.rag_engine: AdaptiveRAGEngine | None = None
        self.actual_expert_id: UUID = uuid4()
        
    async def start(self) -> None:
        """Initialize infrastructure clients and services."""
        logger.info("app.container.start", msg="Initializing application container")
        
        # PostgreSQL
        self.pg_engine = create_async_engine(self.settings.postgres.dsn)
        self.async_session_maker = async_sessionmaker(self.pg_engine, expire_on_commit=False)
        
        # Qdrant
        api_key_str = self.settings.qdrant.api_key.get_secret_value() if self.settings.qdrant.api_key else None
        
        self.qdrant_client = AsyncQdrantClient(
            host=self.settings.qdrant.host,
            port=self.settings.qdrant.port,
            api_key=api_key_str
        )
        
        # Read the actual expert_id from the ingestion pipeline mock
        if os.path.exists("scratch/expert_id.txt"):
            with open("scratch/expert_id.txt", "r") as f:
                self.actual_expert_id = UUID(f.read().strip())
                
        snapshot = RetrievalVersionSnapshot(
            expert_id=self.actual_expert_id,
            expert_version="1.0",
            embedding_model=self.settings.embedding.model,
            embedding_model_version=self.settings.embedding.model_version,
            embedding_dimension=self.settings.embedding.dimension,
            reranker_model="mock",
            reranker_model_version="1",
            semantic_top_k=5,
            lexical_top_k=0,
            rerank_top_k=3,
            strategy=RetrievalStrategy.SEMANTIC
        )
        
        self.rag_engine = AdaptiveRAGEngine(
            semantic_retriever=QdrantSemanticRetriever(client=self.qdrant_client),
            lexical_retriever=MockLexicalRetriever(),
            version_snapshot=snapshot
        )
        
        logger.info("app.container.started", msg="Application container started successfully")
        
    async def stop(self) -> None:
        """Close infrastructure clients gracefully."""
        logger.info("app.container.stop", msg="Stopping application container")
        if self.pg_engine:
            await self.pg_engine.dispose()
        if self.qdrant_client:
            await self.qdrant_client.close()
        logger.info("app.container.stopped", msg="Application container stopped")

    def get_db_session(self) -> AsyncSession:
        """Create a new database session."""
        if not self.async_session_maker:
            raise RuntimeError("Database not initialized")
        return self.async_session_maker()
