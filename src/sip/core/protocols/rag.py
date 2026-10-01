"""RAG Engine Protocols.

These interfaces define the canonical RAG components.
The orchestrator must depend ONLY on these protocols.
"""

from typing import Protocol, List
from uuid import UUID

from sip.core.contracts.rag import (
    Context,
    Evidence,
    EvidenceSufficiencyAssessment,
    Query,
    QueryAnalysis,
    RetrievalCandidate,
    RetrievalPlan,
    RetrievalResult,
)


class QueryAnalyzerProtocol(Protocol):
    async def analyze(self, query: Query) -> QueryAnalysis: ...

class RetrievalPlannerProtocol(Protocol):
    async def plan(self, analysis: QueryAnalysis) -> RetrievalPlan: ...

class ResultFusionProtocol(Protocol):
    async def fuse(
        self, semantic_cands: List[RetrievalCandidate], lexical_cands: List[RetrievalCandidate], plan: RetrievalPlan
    ) -> RetrievalResult: ...

class CandidateDeduplicatorProtocol(Protocol):
    async def deduplicate(self, candidates: List[RetrievalCandidate]) -> List[RetrievalCandidate]: ...

class RerankerProtocol(Protocol):
    async def rerank(self, query: Query, result: RetrievalResult, plan: RetrievalPlan) -> List[Evidence]: ...

class ContextOptimizerProtocol(Protocol):
    async def optimize(self, query: Query, evidence: List[Evidence]) -> Context: ...

class EvidenceEvaluatorProtocol(Protocol):
    async def evaluate(self, query: Query, evidence: List[Evidence]) -> EvidenceSufficiencyAssessment: ...

class EvidenceGateProtocol(Protocol):
    async def enforce(self, assessment: EvidenceSufficiencyAssessment) -> bool: ...

class MetadataFilterProtocol(Protocol):
    def build_filter(self, analysis: QueryAnalysis) -> dict[str, str | list[str]]: ...
