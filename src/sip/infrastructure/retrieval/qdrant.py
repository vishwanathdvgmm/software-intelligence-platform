"""Qdrant implementation of the SemanticRetriever protocol."""

from uuid import UUID

from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models as rest

from sip.core.contracts.knowledge import KnowledgeRecord
from sip.core.protocols.retrieval import SemanticRetriever


class QdrantSemanticRetriever(SemanticRetriever):
    """Retrieves semantic chunks from Qdrant.

    Assumes that the full KnowledgeRecord is stored as a serialized JSON
    in the payload field `knowledge_record_json`, allowing fast,
    storage-agnostic retrieval without requiring a PostgreSQL join.
    """

    def __init__(
        self,
        client: AsyncQdrantClient,
        collection_name: str = "sip_knowledge",
    ) -> None:
        """Initialize the Qdrant retriever.

        Args:
            client: An AsyncQdrantClient instance.
            collection_name: The name of the Qdrant collection.
        """
        self._client = client
        self._collection_name = collection_name

    async def search(
        self,
        query_vector: list[float],
        expert_id: UUID,
        version_filter: dict[str, str | list[str]],
        top_k: int,
    ) -> list[tuple[KnowledgeRecord, float]]:
        """Search for semantically similar chunks.

        Applies expert_id scoping and version_filter via Qdrant payload filters.
        """
        must_conditions: list[rest.Condition] = []

        # 1. Expert scoping (e.g. must match software_id associated with expert)
        # Note: The actual expert_id -> software_id resolution should happen before
        # this call, or we assume `expert_id` is stored in the payload.
        # Assuming `expert_id` is added to the chunk payload during ingestion.
        must_conditions.append(
            rest.FieldCondition(
                key="expert_id",
                match=rest.MatchValue(value=str(expert_id)),
            )
        )

        # 2. Version filtering
        # version_filter: {"major": "26", "minor": ["0", "1"]}
        for key, value in version_filter.items():
            if isinstance(value, list):
                must_conditions.append(
                    rest.FieldCondition(
                        key=f"version_{key}",
                        match=rest.MatchAny(any=value),
                    )
                )
            else:
                must_conditions.append(
                    rest.FieldCondition(
                        key=f"version_{key}",
                        match=rest.MatchValue(value=value),
                    )
                )

        query_filter = rest.Filter(must=must_conditions)

        # Execute search
        results = await self._client.query_points(
            collection_name=self._collection_name,
            query=query_vector,
            query_filter=query_filter,
            limit=top_k,
            with_payload=True,
            with_vectors=False,
        )

        # Parse KnowledgeRecord from payload
        records: list[tuple[KnowledgeRecord, float]] = []
        for scored_point in results.points:
            payload = scored_point.payload or {}

            # The ingestion pipeline must store the serialized record here
            record_json = payload.get("knowledge_record_json")
            if not record_json:
                continue

            try:
                if isinstance(record_json, str):
                    # It might be a stringified JSON
                    record = KnowledgeRecord.model_validate_json(record_json)
                else:
                    # It might be a parsed dict
                    record = KnowledgeRecord.model_validate(record_json)

                records.append((record, scored_point.score))
            except Exception:
                # Log parsing error in a real system
                pass

        return records
