"""Retrieval Planner."""

from sip.core.contracts.rag import (
    QueryAnalysis,
    QueryType,
    RetrievalPlan,
    RetrievalStrategy,
    RetrievalVersionSnapshot,
)

class RetrievalPlanner:
    """Plans the retrieval strategy based on query analysis."""

    def __init__(self, current_version_snapshot: RetrievalVersionSnapshot) -> None:
        """Initialize with the current system state snapshot."""
        self.snapshot = current_version_snapshot

    async def plan(self, analysis: QueryAnalysis) -> RetrievalPlan:
        """Create a retrieval plan for the analyzed query."""
        # Heuristics for M2

        strategy = RetrievalStrategy.HYBRID
        rationale = "Default hybrid retrieval for maximum recall."

        # If it's highly specific like an error message, lean on lexical
        if analysis.query_type == QueryType.TROUBLESHOOTING:
            strategy = RetrievalStrategy.HYBRID
            rationale = "Hybrid selected for troubleshooting to catch exact error strings."

        # Build filter from version constraints
        version_filter: dict[str, str | list[str]] = {}
        if analysis.version_constraints:
            version_filter["software_version"] = list(analysis.version_constraints)

        return RetrievalPlan(
            query_id=analysis.query_id,
            strategy=strategy,
            semantic_top_k=20,
            lexical_top_k=20,
            rerank_top_k=10,
            rrf_k=60,
            version_filter=version_filter,
            rationale=rationale,
            version_snapshot=self.snapshot,
        )
