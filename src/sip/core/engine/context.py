"""Context Optimizer."""

import time

from sip.core.contracts.rag import Context, Evidence, Query

class ContextOptimizer:
    """Optimizes evidence into a final context string for the LLM."""

    def __init__(self, max_tokens: int = 4000) -> None:
        """Initialize with a token budget."""
        self.max_tokens = max_tokens

    def _estimate_tokens(self, text: str) -> int:
        """Heuristic token count estimation.

        For production (M3+), this should use tiktoken or similar.
        """
        return len(text) // 4

    async def optimize(self, query: Query, evidence_list: list[Evidence]) -> Context:
        """Filter, format, and trim evidence to fit the token budget."""
        start_time = time.perf_counter()

        included_evidence = []
        current_tokens = 0
        rendered_parts = []
        truncated = False
        items_removed = 0

        for evidence in evidence_list:
            # Format the evidence chunk
            # In a real system, we might include headers, source links, etc.
            text_content = evidence.knowledge_record.chunk.text
            doc_id = evidence.knowledge_record.document.id

            chunk_text = f"--- Source Document ID: {doc_id} ---\n{text_content}\n"
            chunk_tokens = self._estimate_tokens(chunk_text)

            if current_tokens + chunk_tokens > self.max_tokens:
                truncated = True
                items_removed += 1
                continue

            included_evidence.append(evidence)
            rendered_parts.append(chunk_text)
            current_tokens += chunk_tokens

        rendered_text = "\n".join(rendered_parts)
        latency = (time.perf_counter() - start_time) * 1000

        return Context(
            query_id=query.id,
            evidence_items=tuple(included_evidence),
            rendered_text=rendered_text,
            token_count=current_tokens,
            truncated=truncated,
            items_removed=items_removed
            + (len(evidence_list) - len(included_evidence) - items_removed),
            optimization_latency_ms=latency,
        )
