### Overall SIP Tracker

```
╔════════════════════════════════════════════════════════════╗
║             SOFTWARE INTELLIGENCE PLATFORM                 ║
║                  IMPLEMENTATION ROADMAP                    ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║  PHASE 1  → Product Definition - Completed                 ║
║  PHASE 2  → System Architecture - Completed                ║
║  PHASE 3  → Adaptive RAG Engine - Completed                ║
║  PHASE 4  → Data Layer & Knowledge Storage - In Progress   ║
║  PHASE 5  → Knowledge Ingestion & Crawling                 ║
║  PHASE 6  → Expert System & Expert Lifecycle               ║
║  PHASE 7  → LLM Gateway, Tools & Agent Runtime             ║
║  PHASE 8  → Desktop Application Architecture               ║
║  PHASE 9  → Evaluation, Benchmarking & Observability       ║
║  PHASE 10 → Security, Deployment & Enterprise              ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
```

> **Project**: Software Intelligence Platform
>
> **Phase**: 4

## 4.1 Phase Objective

Phase 4 will define the complete persistence architecture for SIP's knowledge system.

It must support:

- multiple software experts
- software/version separation
- document versioning
- chunk-level retrieval
- semantic embeddings
- BM25S lexical indexing
- metadata filtering
- source provenance
- citations
- incremental updates
- deletion
- synchronization
- consistency
- reproducibility
- rollback
- future scaling

---

## 4.2 Core Storage Architecture

SIP will use **different storage systems for different responsibilities**.

```text
                    SIP KNOWLEDGE
                         │
          ┌──────────────┼──────────────┐
          ↓              ↓              ↓
     PostgreSQL        Qdrant      Object Storage
          │              │              │
 Structured/System    Vectors +       Raw files +
      Metadata         Payloads        artifacts
          │              │
          └───────┬──────┘
                  ↓
               Redis
          Cache / transient
```

### Responsibility

| Storage        | Responsibility                                    |
| -------------- | ------------------------------------------------- |
| PostgreSQL     | Source of truth for structured knowledge metadata |
| Qdrant         | Vector retrieval index                            |
| Object Storage | Original documents and raw artifacts              |
| Redis          | Cache and transient state                         |

Important:

> **Qdrant is a retrieval index, not the authoritative knowledge database.**

---

## 4.3 Knowledge Hierarchy

The canonical hierarchy is:

```text
Software
   ↓
Expert
   ↓
Source
   ↓
Document
   ↓
Document Version
   ↓
Section
   ↓
Chunk
   ↓
Embedding / Index Entry
```

This hierarchy must remain traceable.

Example:

```text
Docker
 ↓
Docker Expert
 ↓
Docker Official Documentation
 ↓
Compose Documentation
 ↓
Version 2.40
 ↓
Networking Section
 ↓
Chunk #1842
 ↓
Embedding
```

---

## 4.4 Software Entity

A software entity represents the product that SIP is building expertise around.

Example:

```text
Docker
VS Code
PostgreSQL
Kubernetes
```

Conceptual fields:

```text
software_id
name
slug
description
vendor
official_domain
status
created_at
updated_at
```

The `software_id` becomes the root identifier for expert-specific knowledge.

---

## 4.5 Software Version

Software versions must be first-class data.

Example:

```text
Docker
├── 26.x
├── 27.x
├── 28.x
└── latest
```

Conceptual fields:

```text
version_id
software_id
version_string
release_date
is_latest
status
created_at
```

This is critical because software knowledge is **version-sensitive**.

---

## 4.6 Expert Identity

The Software Intelligence Platform is based around software-specific experts.

Therefore:

```text
Expert
   ↓
Software
   ↓
Knowledge Scope
```

An expert should reference the software identity rather than duplicating software information.

Conceptually:

```text
expert_id
software_id
expert_name
configuration
status
created_at
updated_at
```

Phase 4 stores the relationship.

The actual expert orchestration remains outside the data layer.

---

## 4.7 Source Model

A source represents where knowledge originates.

Examples:

```text
Official Documentation
GitHub Repository
GitHub Issues
Stack Overflow
Reddit
YouTube Transcript
Release Notes
Blog
```

Conceptual fields:

```text
source_id
source_type
name
base_url
authority_level
status
created_at
updated_at
```

The system must retain source identity for provenance.

---

## 4.8 Source Authority

Sources should carry an authority classification.

For example:

```text
OFFICIAL
PRIMARY
COMMUNITY
SECONDARY
```

This is **metadata**, not an automatic truth guarantee.

The retrieval and generation layers can use this information when evaluating evidence.

---

## 4.9 Document Model

A document represents a logical knowledge resource.

Examples:

```text
Docker Compose Networking Documentation
Docker CLI Reference
Docker Release Notes
GitHub Issue #12345
Stack Overflow Question #12345
```

Conceptual fields:

```text
document_id
source_id
software_id
title
canonical_url
document_type
language
status
created_at
updated_at
```

A document is distinct from its versions.

---

## 4.10 Document Version Model

A document may change over time.

Therefore:

```text
Document
   │
   ├── Version 1
   ├── Version 2
   ├── Version 3
   └── Version 4
```

Conceptual fields:

```text
document_version_id
document_id
software_version_id
content_hash
version_label
published_at
retrieved_at
is_current
status
```

`content_hash` is important for change detection.

---

## 4.11 Why Document Versioning Matters

Suppose:

```text
Docker documentation
```

changes today.

We must know:

```text
What changed?
Which version was retrieved?
Which chunks came from that version?
Which answer used those chunks?
```

Without versioning, historical retrieval becomes unreliable.

---

## 4.12 Content Hashing

Every ingested document version should have a deterministic content hash.

Conceptually:

```text
Normalized Content
       ↓
   Hash Function
       ↓
content_hash
```

This enables:

- duplicate detection
- change detection
- idempotent ingestion
- version creation
- synchronization checks

---

## 4.13 Section Model

Documents should retain structural hierarchy where available.

Example:

```text
Docker Documentation
│
├── Networking
│   ├── Bridge Networks
│   ├── Host Networks
│   └── Overlay Networks
│
└── Storage
    ├── Volumes
    └── Bind Mounts
```

Conceptual fields:

```text
section_id
document_version_id
parent_section_id
title
heading_level
position
```

This structural information improves context reconstruction.

---

## 4.14 Chunk Model

Chunks are the fundamental retrieval units.

Each chunk must maintain its relationship to:

```text
Software
Source
Document
Document Version
Section
```

Conceptual fields:

```text
chunk_id
section_id
document_version_id
chunk_index
text
token_count
content_hash
metadata
created_at
```

---

## 4.15 Chunking Principle

Chunking must preserve semantic and structural coherence.

We should avoid arbitrary splitting like:

```text
Every 500 characters
```

without considering document structure.

The exact chunking algorithm will be implemented in the ingestion/indexing phase.

Phase 4 only defines the persistence contract.

---

## 4.16 Chunk Identity

Every chunk requires a stable identifier.

Example:

```text
chunk_id = UUID
```

The ID must not depend solely on its vector position.

This allows:

- citations
- updates
- deletion
- provenance
- evaluation
- debugging

---

## 4.17 Embedding Model

Embeddings are derived from chunk content.

Conceptually:

```text
Chunk
 ↓
Embedding Model
 ↓
Vector
```

The embedding metadata must identify:

```text
embedding_model
embedding_dimension
embedding_version
created_at
```

This is necessary because changing the embedding model can invalidate an existing vector index.

---

## 4.18 Embedding Versioning

Example:

```text
Embedding Model A
       ↓
Embedding Version 1
       ↓
Qdrant Index
```

Later:

```text
Embedding Model B
       ↓
Embedding Version 2
       ↓
New Qdrant Index
```

The system must never silently mix incompatible embedding spaces.

---

## 4.19 Qdrant Architecture

Qdrant will be used as the semantic retrieval index.

Conceptually:

```text
                    Qdrant
                      │
                 Collection
                      │
               ┌──────┴──────┐
               ↓             ↓
            Vector         Payload
               │             │
               │       software_id
               │       version_id
               │       document_id
               │       chunk_id
               │       source_id
               │       metadata
               │
             Search
```

---

## 4.20 Qdrant Point

Each chunk indexed semantically corresponds to a Qdrant point.

Conceptually:

```text
Point
├── point_id
├── vector
└── payload
```

The payload must contain enough metadata for filtered retrieval and provenance mapping.

---

## 4.21 Qdrant Payload

Minimum payload concept:

```text
chunk_id
document_id
document_version_id
software_id
software_version_id
source_id
section_id
source_type
document_type
language
```

Additional metadata can be added as required.

---

## 4.22 Qdrant Is Not Source of Truth

Important architecture rule:

```text
PostgreSQL
     ↓
Canonical Metadata
```

while:

```text
Qdrant
     ↓
Retrieval Index
```

If Qdrant is lost:

```text
PostgreSQL + source artifacts
          ↓
      Re-index
          ↓
        Qdrant
```

The system should be recoverable.

---

## 4.23 BM25S Index

BM25S requires a lexical representation of the indexed knowledge.

The lexical index should be treated as another **derived retrieval index**, not the canonical source of truth.

Conceptually:

```text
PostgreSQL / Knowledge Records
             │
             ├──────────→ Qdrant
             │
             └──────────→ BM25S Index
```

The BM25S index must preserve the `chunk_id` mapping.

Thus:

```text
BM25S result
    ↓
chunk_id
    ↓
PostgreSQL metadata
```

---

## 4.24 Object Storage

Original source artifacts should be retained separately.

Examples:

```text
PDF
HTML snapshot
Markdown
JSON
YouTube transcript
Downloaded documentation
Raw API response
```

Conceptually:

```text
Object Storage
│
├── source/
├── document/
├── version/
└── artifacts/
```

The exact provider can remain configurable.

---

## 4.25 Raw Artifact vs Normalized Content

We must distinguish:

```text
RAW
```

from:

```text
NORMALIZED
```

Example:

```text
Website HTML
     ↓
Raw Artifact
     ↓
Parser
     ↓
Normalized Document
     ↓
Sections
     ↓
Chunks
```

This allows reprocessing without downloading the source again.

---

## 4.26 Redis

Redis will **not** be the authoritative knowledge store.

Its responsibilities may include:

- query cache
- retrieval cache
- embedding cache
- temporary processing state
- job coordination
- rate limiting
- short-lived locks

Persistent knowledge remains in PostgreSQL/object storage/indexes.

---

## 4.27 PostgreSQL Responsibilities

PostgreSQL should contain authoritative structured metadata.

Major entities:

```text
software
software_versions
experts
sources
documents
document_versions
sections
chunks
embeddings_metadata
index_records
ingestion_runs
```

Additional tables may be introduced when required.

---

## 4.28 Core Relationships

```text
Software
   │
   ├──────────< SoftwareVersion
   │
   ├──────────< Expert
   │
   ├──────────< Source
   │
   └──────────< Document
                    │
                    └──────< DocumentVersion
                                  │
                                  └──────< Section
                                               │
                                               └──────< Chunk
```

This is the primary relational hierarchy.

---

## 4.29 Provenance Relationship

Every chunk must be traceable:

```text
Chunk
 ↓
Section
 ↓
Document Version
 ↓
Document
 ↓
Source
 ↓
Canonical URL
```

Therefore an answer citation can point back to its original source.

---

## 4.30 Index Mapping

The same chunk may exist in multiple derived indexes.

```text
                 Chunk
                   │
        ┌──────────┼──────────┐
        ↓          ↓          ↓
     Qdrant      BM25S     Metadata
      Point       Entry      Record
```

All must reference the same canonical `chunk_id`.

This is a critical invariant.

---

## 4.31 Index Consistency

The system must prevent situations such as:

```text
PostgreSQL → Chunk A
Qdrant     → Old Chunk A
BM25S      → Chunk B
```

Therefore every indexing operation must be trackable.

Conceptual state:

```text
PENDING
INDEXING
INDEXED
FAILED
STALE
DELETED
```

---

## 4.32 Knowledge Lifecycle

A knowledge item follows:

```text
DISCOVERED
    ↓
ACQUIRED
    ↓
NORMALIZED
    ↓
VERSIONED
    ↓
CHUNKED
    ↓
INDEXED
    ↓
ACTIVE
    ↓
UPDATED / SUPERSEDED
    ↓
ARCHIVED
```

The ingestion system will execute this lifecycle.

Phase 4 defines the persisted states.

---

## 4.33 Update Lifecycle

When source content changes:

```text
Old Document Version
        ↓
Change Detection
        ↓
New Document Version
        ↓
New Chunks
        ↓
New Embeddings
        ↓
Qdrant Update
        ↓
BM25S Update
        ↓
Old Index Entries
      removed/deactivated
```

The system must not overwrite historical versions blindly.

---

## 4.34 Incremental Indexing

If only 5 chunks changed out of 10,000:

```text
DO NOT

re-index 10,000 chunks
```

unless required by an embedding/index configuration change.

Prefer:

```text
Changed chunks
     ↓
Re-embed
     ↓
Update affected indexes
```

This is important for scalability.

---

## 4.35 Deletion

Deletion must be traceable.

When a document is removed:

```text
Document
 ↓
Document Version
 ↓
Chunks
 ↓
Qdrant Points
 ↓
BM25S Entries
```

must be handled consistently.

The canonical metadata should record deletion state rather than relying only on physical removal.

---

## 4.36 Re-indexing

A full re-index may be required when:

- embedding model changes
- embedding dimensions change
- chunking strategy changes
- retrieval metadata changes
- Qdrant configuration changes
- BM25S configuration changes

The system should support rebuilding derived indexes from canonical knowledge.

---

## 4.37 Data Integrity Invariants

The following must always hold:

### Invariant 1

Every chunk belongs to exactly one document version.

### Invariant 2

Every document version belongs to exactly one document.

### Invariant 3

Every document belongs to a source and software scope.

### Invariant 4

Every Qdrant point maps to a valid chunk.

### Invariant 5

Every BM25S result maps to a valid chunk.

### Invariant 6

Deleted/obsolete knowledge must not silently remain retrievable.

### Invariant 7

Embedding models must not be mixed within an incompatible vector index.

### Invariant 8

Every citation must be traceable to persisted provenance.

---

## 4.38 Database Transactions

Operations affecting authoritative relational data should use appropriate PostgreSQL transactions.

Example:

```text
Create Document Version
        ↓
Create Sections
        ↓
Create Chunks
        ↓
Commit
```

Derived index operations can then occur based on the committed state.

---

## 4.39 Indexing Transaction Boundary

Qdrant/BM25S updates should not be treated as identical to PostgreSQL transactions.

Instead:

```text
PostgreSQL Commit
       ↓
Index Job
       ↓
Qdrant
       +
BM25S
```

Index state should be tracked so failed indexing can be retried.

---

## 4.40 Knowledge Snapshot

The system should be capable of identifying the knowledge state used for a retrieval run.

Conceptually:

```text
Retrieval Run
   ↓
Knowledge Snapshot
   ↓
Document Versions
   ↓
Chunks
```

This improves reproducibility.

---

## 4.41 Reproducibility

Given:

```text
Query
+
Expert
+
Knowledge Snapshot
+
Retrieval Configuration
+
Embedding Version
```

the system should be able to explain which evidence was available during retrieval.

This is important for evaluation and debugging.

---

## 4.42 Data Security

The data layer must enforce expert boundaries.

A query for:

```text
Docker Expert
```

must not accidentally retrieve:

```text
VS Code Expert
```

knowledge.

Every retrieval index therefore needs software/expert scoping metadata.

---

## 4.43 Privacy

If future knowledge sources contain user-specific or private data, the system must support source-level access boundaries.

Private knowledge must not automatically become globally retrievable.

---

## 4.44 Backup Strategy

Backup responsibilities:

### PostgreSQL

Regular database backups.

### Object Storage

Versioned artifact retention.

### Qdrant

Either backup directly or rebuild from canonical data.

### BM25S

Rebuildable derived index.

### Redis

Generally treated as disposable/rebuildable unless a specific persistent workflow requires otherwise.

---

## 4.45 Recovery Principle

The recovery hierarchy is:

```text
                Canonical Knowledge
                       │
          ┌────────────┴────────────┐
          ↓                         ↓
    PostgreSQL                 Object Storage
          │
          ↓
   Rebuild Derived Indexes
       /           \
      ↓             ↓
   Qdrant         BM25S
```

The architecture should prefer **reconstruction over permanent dependence on derived indexes**.

---

## 4.46 Phase 3 Integration

Phase 3 expects:

```text
Semantic Retrieval
BM25S Retrieval
Metadata Filtering
Provenance
Version Filtering
```

Phase 4 provides those storage capabilities.

Therefore:

```text
Phase 4
   ↓
Data + Indexes
   ↓
Phase 3 Adaptive RAG
```

---

## 4.47 Phase 5 Integration

Phase 5 will later handle knowledge acquisition and processing.

Its output must eventually create/update:

```text
Source
Document
Document Version
Section
Chunk
Embedding
Index Entries
```

Phase 5 must use Phase 4's persistence contracts rather than inventing separate storage structures.

---

## 4.48 Recommended PostgreSQL Logical Schema

Initial schema:

```text
software
software_versions
experts

sources
documents
document_versions
sections
chunks

embedding_models
chunk_embeddings

index_records
ingestion_runs
```

Potentially later:

```text
knowledge_snapshots
retrieval_runs
citation_records
```

but these should only be added to Phase 4 if later implementation requirements justify persistence at this layer.

---

## 4.49 Recommended Identifier Strategy

Use stable UUID-based identifiers for primary entities.

Examples:

```text
software_id
version_id
source_id
document_id
document_version_id
section_id
chunk_id
```

External IDs such as:

```text
GitHub issue number
URL
YouTube video ID
```

should remain metadata rather than replacing internal identifiers.

---

## 4.50 Phase 4 Implementation Order

Implementation should proceed in this order:

```text
1. PostgreSQL connection/configuration
             ↓
2. Core relational models
             ↓
3. Database migrations
             ↓
4. Source + Document models
             ↓
5. Version + Section models
             ↓
6. Chunk model
             ↓
7. Embedding metadata
             ↓
8. Qdrant integration
             ↓
9. Qdrant payload contract
             ↓
10. BM25S index mapping
             ↓
11. Object storage abstraction
             ↓
12. Redis abstraction
             ↓
13. Index-state tracking
             ↓
14. Update/delete lifecycle
             ↓
15. Re-indexing
             ↓
16. Backup/recovery validation
```

---

## 4.51 Phase 4 Completion Criteria

Phase 4 is complete when:

- [ ] PostgreSQL architecture defined
- [ ] Core relational entities defined
- [ ] Software/version hierarchy defined
- [ ] Expert relationship defined
- [ ] Source model defined
- [ ] Document model defined
- [ ] Document versioning defined
- [ ] Section model defined
- [ ] Chunk model defined
- [ ] Provenance chain defined
- [ ] Embedding metadata defined
- [ ] Qdrant architecture defined
- [ ] Qdrant payload contract defined
- [ ] BM25S index mapping defined
- [ ] Object storage responsibility defined
- [ ] Redis responsibility defined
- [ ] Index synchronization defined
- [ ] Incremental updates defined
- [ ] Deletion lifecycle defined
- [ ] Re-indexing strategy defined
- [ ] Data integrity invariants defined
- [ ] Backup/recovery strategy defined
- [ ] Security boundaries defined
- [ ] Phase 3 integration contract defined
- [ ] Phase 5 integration contract defined

---

## 4.52 Final Phase 4 Architecture

```text
                         KNOWLEDGE SYSTEM
                                │
                ┌───────────────┼────────────────┐
                │               │                │
                ▼               ▼                ▼
          PostgreSQL         Object Storage      Redis
          ──────────         ──────────────      ─────
          Software           Raw Files           Cache
          Versions           HTML/PDF            Jobs
          Sources            Snapshots           Locks
          Documents          Artifacts           Temp State
          Sections
          Chunks
          Provenance
          Index State
                │
                │
                ├───────────────┐
                │               │
                ▼               ▼
             Qdrant           BM25S
             ──────           ─────
             Vectors          Lexical
             Payload          Index
                │               │
                └───────┬───────┘
                        ▼
                PHASE 3
              ADAPTIVE RAG
                        │
                        ▼
                   LLM GATEWAY
```
