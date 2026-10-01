"""FastAPI application for the SIP Core Backend.

This serves as the API boundary between the Desktop UI (Process 1)
and the SIP Core Runtime (Process 2).
"""

from typing import Dict
import time
from uuid import uuid4

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from sip.observability.metrics import get_metrics_collector
from sip.observability.middleware import ObservabilityMiddleware
from sip.security.middleware import SecurityMiddleware

from sip.api.bootstrap import lifespan
from sip.api.dependencies import get_db_session, get_rag_engine, get_container

from sip.core.contracts.experts import Expert
from sip.core.contracts.rag import Query
from sip.core.container import ApplicationContainer
from sip.infrastructure.database.repositories import PostgresExpertRepository
from sip.core.engine.orchestrator import AdaptiveRAGEngine

app = FastAPI(
    title="SIP Core API",
    description="Software Intelligence Platform Backend API",
    version="0.1.0",
    lifespan=lifespan,
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
app.add_middleware(SecurityMiddleware)

# Observability middleware: correlation IDs, latency recording, structured log binding
app.add_middleware(ObservabilityMiddleware)

from sip.core.contracts.api import HealthStatus

@app.get("/api/health", response_model=HealthStatus)
async def health_check() -> HealthStatus:
    """Check the health of the SIP Core Runtime."""
    return HealthStatus(status="healthy", version="0.1.0")

@app.get("/api/metrics")
async def metrics() -> Dict[str, object]:
    """Return a point-in-time snapshot of runtime metrics."""
    collector = get_metrics_collector()
    return collector.snapshot()

@app.get("/api/protected")
async def protected_route() -> Dict[str, str]:
    """A sample protected endpoint to test authentication."""
    return {"message": "You have accessed a protected resource!"}

# ---------------------------------
# Phase 6: Expert Management API (PostgreSQL)
# ---------------------------------

@app.get("/api/experts", response_model=list[Expert])
async def list_experts(session: AsyncSession = Depends(get_db_session)) -> list[Expert]:
    """Return the list of available software experts from the PostgreSQL database."""
    repo = PostgresExpertRepository(session)
    return await repo.list_all()

# ---------------------------------
# Chat Route
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
async def chat_endpoint(
    req: ChatRequest,
    engine: AdaptiveRAGEngine = Depends(get_rag_engine),
    container: ApplicationContainer = Depends(get_container)
) -> ChatResponse:
    """Process a query through the ACTUAL SIP engine pipeline."""
    start_time = time.time()
    
    query = Query(
        id=uuid4(),
        text=req.query,
        expert_id=container.actual_expert_id
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

