"""Query Analysis, Classification, and Transformation."""

from sip.core.contracts.rag import Query, QueryAnalysis, QueryComplexity, QueryType


class QueryAnalyzer:
    """Analyzes a query to extract entities, intent, and complexity.

    This is a heuristic implementation for M2. A true LLM-based implementation
    will be provided in Phase 3.
    """

    async def analyze(self, query: Query) -> QueryAnalysis:
        """Analyze the query."""
        # Simple heuristics for M2 testing
        text = query.text.lower()

        # Classification
        query_type = QueryType.FACTUAL
        if "how to" in text or "steps" in text:
            query_type = QueryType.PROCEDURAL
        elif "error" in text or "fail" in text or "issue" in text:
            query_type = QueryType.TROUBLESHOOTING
        elif "vs" in text or "difference" in text or "compare" in text:
            query_type = QueryType.COMPARISON

        # Complexity
        complexity = QueryComplexity.SIMPLE
        if len(text.split()) > 15:
            complexity = QueryComplexity.MODERATE
        if query_type in (QueryType.MULTI_HOP, QueryType.COMPARISON):
            complexity = QueryComplexity.COMPLEX

        # Version specific heuristic
        version_constraints = []
        if "version" in text or "v1" in text or "v2" in text:
            query_type = QueryType.VERSION_SPECIFIC
            version_constraints.append("latest")  # Mock extraction

        return QueryAnalysis(
            query_id=query.id,
            query_type=query_type,
            complexity=complexity,
            entities=(),
            version_constraints=tuple(version_constraints),
            requires_multi_hop=(query_type == QueryType.COMPARISON),
            sub_questions=(),
        )


class QueryTransformer:
    """Transforms, rewrites, and decomposes queries."""

    async def transform(self, query: Query, analysis: QueryAnalysis) -> list[str]:
        """Return a list of sub-queries or rewritten queries."""
        if analysis.requires_multi_hop:
            # Mock decomposition
            return [f"What is part 1 of {query.text}?", f"What is part 2 of {query.text}?"]
        # Default: return the original query text
        return [query.text]
