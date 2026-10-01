"""Metadata Filters."""

from sip.core.contracts.rag import QueryAnalysis

class MetadataFilter:
    """Builds explicit storage-agnostic filters from query analysis."""

    def build_filter(self, analysis: QueryAnalysis) -> dict[str, str | list[str]]:
        """Construct a storage-independent filter dictionary."""
        version_filter: dict[str, str | list[str]] = {}
        if analysis.version_constraints:
            version_filter["version"] = list(analysis.version_constraints)
        return version_filter
