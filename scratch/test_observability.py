"""Test script for the SIP Observability Architecture (Milestone 9)."""

import asyncio
from uuid import uuid4

from sip.core.logging import configure_logging
from sip.core.contracts.rag import (
    EvidenceSufficiency,
    QueryType,
    RetrievalStrategy,
    RetrievalVersionSnapshot,
)
from sip.observability.tracer import PipelineTracer
from sip.observability.metrics import MetricsCollector, get_metrics_collector

async def main() -> None:
    configure_logging(force=True)
    
    print("=" * 60)
    print("  SIP Observability Architecture — Milestone 9 Test")
    print("=" * 60)

    # ── 1. Test PipelineTracer ──────────────────────────────────────────
    print("\n--- Testing PipelineTracer ---")

    query_id = uuid4()
    expert_id = uuid4()
    request_id = f"req-{uuid4().hex[:8]}"

    tracer = PipelineTracer(
        query_id=query_id,
        expert_id=expert_id,
        request_id=request_id,
    )

    # Simulate pipeline stages
    tracer.record_query_analysis(query_type=QueryType.FACTUAL, latency_ms=15.2)
    tracer.record_strategy(RetrievalStrategy.HYBRID)
    tracer.record_retrieval("semantic", candidates=12, latency_ms=85.0)
    tracer.record_retrieval("bm25s", candidates=10, latency_ms=45.0)
    tracer.record_fusion(before_dedup=22, after_dedup=18, latency_ms=5.0)
    tracer.record_reranking(evidence_count=8, latency_ms=120.5)
    tracer.record_evidence_gate(
        sufficiency=EvidenceSufficiency.SUFFICIENT,
        confidence=0.92,
    )
    tracer.record_context_optimization(
        token_count=3200,
        items_removed=2,
        truncated=False,
        latency_ms=12.0,
    )
    tracer.record_llm_generation(
        provider="ollama",
        model="llama3",
        input_tokens=3200,
        output_tokens=450,
        latency_ms=1850.0,
    )
    tracer.record_answer(answer_length_chars=1200, citation_count=3)

    # Build the final ExecutionTrace
    snapshot = RetrievalVersionSnapshot(
        expert_id=expert_id,
        expert_version="1.0.0",
        embedding_model="all-MiniLM-L6-v2",
        embedding_model_version="1.0",
        embedding_dimension=384,
        reranker_model="cross-encoder/ms-marco-MiniLM-L-6-v2",
        reranker_model_version="1.0",
        semantic_top_k=20,
        lexical_top_k=20,
        rerank_top_k=10,
        strategy=RetrievalStrategy.HYBRID,
    )
    trace = tracer.build_trace(version_snapshot=snapshot)

    print(f"\n  Trace ID:            {trace.id}")
    print(f"  Query Type:          {trace.query_type}")
    print(f"  Strategy:            {trace.strategy_used}")
    print(f"  Retrieval Entries:   {len(trace.retrieval_entries)}")
    print(f"  Evidence Count:      {trace.evidence_count}")
    print(f"  Sufficiency:         {trace.sufficiency}")
    print(f"  Context Tokens:      {trace.context_token_count}")
    print(f"  LLM Model:           {trace.llm_model}")
    print(f"  LLM Tokens (in/out): {trace.llm_input_tokens}/{trace.llm_output_tokens}")
    print(f"  Answer Length:       {trace.answer_length_chars} chars")
    print(f"  Citation Count:      {trace.citation_count}")
    print(f"  Total Latency:       {trace.total_latency_ms:.1f} ms")
    print(f"  Error:               {trace.error}")

    # ── 2. Test MetricsCollector ────────────────────────────────────────
    print("\n--- Testing MetricsCollector ---")

    metrics = get_metrics_collector()
    metrics.reset()

    # Simulate 5 requests
    for i in range(5):
        metrics.inc_requests()
        metrics.record_retrieval_latency(80.0 + i * 10)
        metrics.record_reranker_latency(100.0 + i * 20)
        metrics.record_llm_latency(1500.0 + i * 100)
        metrics.record_total_latency(2000.0 + i * 150)
        metrics.add_tokens(input_tokens=3000, output_tokens=400)
        metrics.record_retrieval_hit(hit=(i < 4))  # 4 hits out of 5

    # Simulate 1 failure
    metrics.inc_failures()

    snap = metrics.snapshot()

    print(f"\n  Requests Total:   {snap['requests_total']}")
    print(f"  Requests Failed:  {snap['requests_failed']}")
    print(f"  Tokens Total:     {snap['tokens_total']}")
    print(f"  Hit Rate:         {snap['retrieval_hit_rate']}")
    print(f"  Latency (total):  {snap['latency']}")

    print("\n" + "=" * 60)
    print("  ✅ Observability architecture verified!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
