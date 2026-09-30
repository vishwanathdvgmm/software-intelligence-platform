"""Evidence Evaluator (Evidence Gate)."""

from sip.core.contracts.rag import (
    Evidence,
    EvidenceSufficiency,
    EvidenceSufficiencyAssessment,
    Query,
)

class EvidenceEvaluator:
    """Evaluates whether retrieved evidence is sufficient for generation."""

    async def evaluate(
        self, query: Query, evidence_list: list[Evidence], attempt_number: int = 1
    ) -> EvidenceSufficiencyAssessment:
        """Evaluate the evidence."""
        # Heuristics for M2

        if not evidence_list:
            return EvidenceSufficiencyAssessment(
                query_id=query.id,
                sufficiency=EvidenceSufficiency.INSUFFICIENT,
                confidence=1.0,
                rationale="No evidence was retrieved.",
                attempt_number=attempt_number,
                should_retry=True,
                reformulated_query=f"Please provide more context for: {query.text}",
            )

        # Check highest score
        top_score = evidence_list[0].reranker_score

        # In a real system, the threshold depends on the model.
        # With mock scores (10.0 - i), it will usually be sufficient.

        sufficiency = EvidenceSufficiency.SUFFICIENT
        rationale = "Top evidence score indicates strong relevance."
        should_retry = False

        if top_score < 0.0:  # e.g., low cross-encoder score
            sufficiency = EvidenceSufficiency.INSUFFICIENT
            rationale = "Top evidence score is below threshold."
            should_retry = True

        return EvidenceSufficiencyAssessment(
            query_id=query.id,
            sufficiency=sufficiency,
            confidence=0.9,
            rationale=rationale,
            attempt_number=attempt_number,
            should_retry=should_retry,
        )
