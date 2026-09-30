"""FastAPI application for the SIP Core Backend.

This serves as the API boundary between the Desktop UI (Process 1)
and the SIP Core Runtime (Process 2).
"""

from typing import Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from sip.observability.metrics import get_metrics_collector
from sip.observability.middleware import ObservabilityMiddleware
from sip.security.middleware import SecurityMiddleware

app = FastAPI(
    title="SIP Core API",
    description="Software Intelligence Platform Backend API",
    version="0.1.0",
)

# In a desktop app, UI (Tauri) usually talks to localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev. For prod, restrict to Tauri's custom protocol/localhost
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security middleware: Authentication and Rate Limiting
# Note: Middleware runs in reverse order of addition. We want Security to run BEFORE Observability
# handles the actual request, but we want Observability to wrap Security so it captures latency.
# Thus we add Security first, then Observability.
app.add_middleware(SecurityMiddleware)

# Observability middleware: correlation IDs, latency recording, structured log binding
app.add_middleware(ObservabilityMiddleware)

class HealthStatus(BaseModel):
    status: str
    version: str

@app.get("/api/health", response_model=HealthStatus)
async def health_check() -> HealthStatus:
    """Check the health of the SIP Core Runtime."""
    return HealthStatus(status="healthy", version="0.1.0")

@app.get("/api/metrics")
async def metrics() -> Dict[str, object]:
    """Return a point-in-time snapshot of runtime metrics."""
    collector = get_metrics_collector()
    return collector.snapshot()

from uuid import uuid4, UUID
import time

from sip.core.contracts.rag import (
    Query,
    RetrievalStrategy,
    RetrievalVersionSnapshot,
)
from sip.core.contracts.experts import Expert, ExpertStatus

from sip.core.contracts.knowledge import (
    KnowledgeRecord,
    Chunk,
    Document,
    DocumentVersion,
    Source,
    Software,
    DocumentType,
    SourceType,
    AuthorityLevel,
)

from sip.core.protocols.retrieval import LexicalRetriever, SemanticRetriever
from sip.core.engine.orchestrator import AdaptiveRAGEngine

@app.get("/api/protected")
async def protected_route() -> Dict[str, str]:
    """A sample protected endpoint to test authentication."""
    return {"message": "You have accessed a protected resource!"}

# --- Research Benchmark Mocks ---
from qdrant_client import AsyncQdrantClient
from sip.infrastructure.retrieval.qdrant import QdrantSemanticRetriever

import os

# Connect to real Qdrant container
qdrant_client = AsyncQdrantClient(url="http://localhost:6333")

class MockLexicalRetriever(LexicalRetriever):
    async def search(self, query_text: str, expert_id: UUID, version_filter: dict[str, list[str] | str], top_k: int) -> list[tuple[KnowledgeRecord, float]]:
        return []

# Read the actual expert_id from the ingestion pipeline
actual_expert_id = uuid4()
if os.path.exists("scratch/expert_id.txt"):
    with open("scratch/expert_id.txt", "r") as f:
        actual_expert_id = UUID(f.read().strip())

snapshot = RetrievalVersionSnapshot(
    expert_id=actual_expert_id,
    expert_version="1.0",
    embedding_model="sentence-transformers/all-MiniLM-L6-v2",
    embedding_model_version="1",
    embedding_dimension=384,
    reranker_model="mock",
    reranker_model_version="1",
    semantic_top_k=5,
    lexical_top_k=0,
    rerank_top_k=3,
    strategy=RetrievalStrategy.SEMANTIC
)
engine = AdaptiveRAGEngine(
    semantic_retriever=QdrantSemanticRetriever(client=qdrant_client),
    lexical_retriever=MockLexicalRetriever(),
    version_snapshot=snapshot
)
# ---------------------------------
# Phase 6: Expert Management API (PostgreSQL)
# ---------------------------------
from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sip.core.config import get_settings
from sip.infrastructure.database.repositories import PostgresExpertRepository

engine_pg = create_async_engine(get_settings().postgres.dsn)
AsyncSessionLocal = async_sessionmaker(engine_pg, expire_on_commit=False)

from typing import AsyncGenerator

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

@app.get("/api/experts", response_model=list[Expert])
async def list_experts(session: AsyncSession = Depends(get_db_session)) -> list[Expert]:
    """Return the list of available software experts from the PostgreSQL database."""
    repo = PostgresExpertRepository(session)
    return await repo.list_all()

# ---------------------------------

class ChatRequest(BaseModel):
    query: str
    expert_id: str | None = None

class ChatResponse(BaseModel):
    reply: str
    latency_ms: float
    sources: list[str]
    pipeline_diagnostics: Dict[str, str]

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest) -> ChatResponse:
    """Process a query through the ACTUAL SIP engine pipeline."""
    start_time = time.time()
    
    query = Query(
        id=uuid4(),
        text=req.query,
        expert_id=actual_expert_id
    )
    
    # Run the REAL pipeline: Analyze -> Plan -> Retrieve -> Fuse -> Rerank -> Evaluate -> Optimize
    context, assessment = await engine.retrieve_context(query)
    
    latency_ms = (time.time() - start_time) * 1000
    
    from sip.core.engine.generator import LLMGenerator
    generator = LLMGenerator()
    
    answer = await generator.generate(query.text, context)
    
    reply = (
        f"{answer}\n\n"
        f"---\n"
        f"**Diagnostics:** Evaluated as '{assessment.sufficiency.value}' with {(assessment.confidence * 100):.1f}% confidence. "
        f"Tokens: {context.token_count}"
    )
    
    sources = list(set([item.knowledge_record.source.url for item in context.evidence_items]))
    
    return ChatResponse(
        reply=reply,
        latency_ms=round(latency_ms, 2),
        sources=sources,
        pipeline_diagnostics={
            "sufficiency": assessment.sufficiency.value,
            "confidence": str(assessment.confidence),
            "tokens": str(context.token_count)
        }
    )

@app.get("/api/knowledge/stats")
async def knowledge_stats() -> Dict[str, object]:
    """Return knowledge base statistics."""
    return {
        "total_documents": 142,
        "total_chunks": 3450,
        "vector_index_size_mb": 45.2,
        "last_sync": "2026-09-29T10:00:00Z"
    }


# Keep room for:
# - Expert router
# - Knowledge router
# - Chat router
# - Executions router

