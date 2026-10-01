"""Evidence Gate."""

from sip.core.contracts.rag import EvidenceSufficiency, EvidenceSufficiencyAssessment

class EvidenceGate:
    """Enforces evidence policy."""

    async def enforce(self, assessment: EvidenceSufficiencyAssessment) -> bool:
        """Return True if evidence is sufficient to answer, False otherwise."""
        if assessment.sufficiency == EvidenceSufficiency.SUFFICIENT:
            return True
        return False
