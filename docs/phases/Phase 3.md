### Overall SIP Tracker

```
╔════════════════════════════════════════════════════════════╗
║             SOFTWARE INTELLIGENCE PLATFORM                 ║
║                  IMPLEMENTATION ROADMAP                    ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║  PHASE 1  → Product Definition - Completed                 ║
║  PHASE 2  → System Architecture - Completed                ║
║  PHASE 3  → Adaptive RAG Engine - In Progress              ║
║  PHASE 4  → Data Layer & Knowledge Storage                 ║
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
> **Phase**: 3
>
> **Subsystem**: Adaptive Retrieval-Augmented Generation Engine
>
> **Status**: Implementation Specification
>
> **Primary Goal**: Improve retrieval precision, evidence quality, groundedness and efficiency over a conventional fixed RAG pipeline.

---

## 3.1 Purpose

The Adaptive RAG Engine is the intelligence layer responsible for converting a user query into a set of **relevant, sufficient, version-compatible and traceable evidence** that can be safely passed to the generation layer.

Traditional RAG commonly follows:

```text
Query
 ↓
Embedding
 ↓
Vector Search
 ↓
Top-K Chunks
 ↓
LLM
```

SIP will instead use an adaptive retrieval process:

```text
Query
 ↓
Analyze
 ↓
Classify
 ↓
Transform
 ↓
Plan Retrieval
 ↓
Retrieve
 ↓
Fuse
 ↓
Rerank
 ↓
Optimize Context
 ↓
Evaluate Evidence
 ↓
 ┌───────────────┐
 │ Sufficient?   │
 └───────┬───────┘
       YES│       │NO
          ↓       ↓
        LLM    Retry / Reformulate
          ↓
      Validate
          ↓
      Answer + Citations
```

The central principle is:

> **Retrieval is an adaptive evidence-acquisition process, not a single vector database lookup.**

---

## 3.2 Design Objectives

The Adaptive RAG Engine must optimize for:

1. **Retrieval Precision**
2. **Retrieval Recall**
3. **Evidence Relevance**
4. **Context Quality**
5. **Groundedness**
6. **Version Correctness**
7. **Low Redundancy**
8. **Controlled Latency**
9. **Token Efficiency**
10. **Traceability**
11. **Graceful Failure**
12. **Abstention when evidence is insufficient**

The engine should not optimize only for retrieval similarity.

---

## 3.3 Core Design Principles

### 3.3.1 Query-Adaptive Retrieval

Different queries require different retrieval strategies.

For example:

```text
"What is Docker Compose?"
```

may require straightforward retrieval.

While:

```text
"Why does Docker Compose behave differently between version X and version Y?"
```

requires:

- version awareness
- multiple evidence sources
- comparison
- potentially multiple retrieval passes

Therefore:

> **Retrieval strategy must depend on query characteristics.**

---

### 3.3.2 Hybrid Retrieval

SIP will combine:

### Semantic Retrieval

Captures conceptual similarity.

### Lexical Retrieval

Captures exact terminology, identifiers, error messages, flags, APIs and technical tokens.

The lexical engine will use:

> **BM25S**

not traditional BM25.

Conceptually:

```text
                 Query
                   │
          ┌────────┴─────────┐
          ↓                  ↓
   Semantic Retrieval    BM25S Retrieval
          │                  │
          └────────┬─────────┘
                   ↓
              Result Fusion
```

---

### 3.3.3 Retrieval Is Multi-Stage

Retrieval will not immediately send initial candidates to the LLM.

Instead:

```text
Candidate Generation
        ↓
Candidate Fusion
        ↓
Candidate Reranking
        ↓
Evidence Filtering
        ↓
Context Optimization
        ↓
Generation
```

Each stage reduces uncertainty.

---

### 3.3.4 Evidence Before Generation

The LLM must receive an evidence package rather than an uncontrolled collection of retrieved chunks.

```text
Retrieved Chunks
      ↓
Evidence Evaluation
      ↓
Context Construction
      ↓
LLM
```

---

### 3.3.5 Explicit Evidence Sufficiency

The engine must determine whether the available evidence is sufficient.

Possible outcomes:

```text
SUFFICIENT
INSUFFICIENT
AMBIGUOUS
CONTRADICTORY
STALE
VERSION_MISMATCH
```

This status becomes part of the retrieval result.

---

### 3.3.6 Abstention

If sufficient evidence cannot be obtained after permitted retrieval attempts, the system must be able to abstain.

```text
Query
 ↓
Retrieve
 ↓
Evidence insufficient
 ↓
Retry
 ↓
Evidence insufficient
 ↓
Abstain
```

The engine must never treat:

> “The LLM can probably answer”

as evidence sufficiency.

---

## 3.4 High-Level Architecture

```text
┌─────────────────────────────┐
│         User Query          │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│      Query Analyzer         │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│     Query Classifier        │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│    Query Transformer        │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│    Retrieval Planner        │
└──────────────┬──────────────┘
               ↓
       ┌───────┴────────┐
       ↓                ↓
 Semantic Search      BM25S
       │                │
       └───────┬────────┘
               ↓
┌─────────────────────────────┐
│       Result Fusion         │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│     Cross-Encoder           │
│        Reranker             │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│    Context Optimizer        │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│    Evidence Evaluator       │
└──────────────┬──────────────┘
               ↓
          ┌────┴─────┐
          │ Sufficient│
          └────┬─────┘
           YES │ NO
               │
          ┌────┴─────────────┐
          ↓                  ↓
      Generation       Retry / Reformulate
          ↓
      Validation
          ↓
   Answer + Citations
```

---

## 3.5 Query Analyzer

The Query Analyzer extracts characteristics required for retrieval planning.

It should identify:

- entities
- software names
- software versions
- technical terminology
- error codes
- commands
- file names
- APIs
- configuration parameters
- intent
- query complexity
- temporal requirements
- comparison requirements

Example:

```text
Query:

"Why is Docker Compose v2 failing with
'network not found' after upgrading?"
```

Possible analysis:

```text
Software: Docker Compose
Version: v2
Intent: Troubleshooting
Error: network not found
Operation: Upgrade
Complexity: Medium
Temporal sensitivity: High
Exact-term importance: High
```

---

## 3.6 Query Classification

The query should be classified into one or more retrieval-relevant categories.

Possible categories:

### Factual

```text
"What is Docker Compose?"
```

### Procedural

```text
"How do I create a Docker network?"
```

### Troubleshooting

```text
"Why am I getting this Docker error?"
```

### Comparison

```text
"What is the difference between X and Y?"
```

### Version-Specific

```text
"How does Docker 27 handle this?"
```

### Multi-Hop

```text
"Why did changing X cause Y?"
```

### Exploratory

```text
"What are the security implications of this feature?"
```

A query may belong to multiple categories.

---

## 3.7 Query Transformation

Depending on classification, the query may be transformed.

Operations include:

- rewriting
- expansion
- decomposition
- terminology normalization
- error-term extraction
- entity extraction
- sub-question generation

Example:

```text
Original:

"Why does it fail after upgrading?"

Possible transformed queries:

Q1:
"What software was upgraded?"

Q2:
"What changed in the new version?"

Q3:
"What causes the reported failure?"

Q4:
"Are there known compatibility issues?"
```

The transformation process must preserve the original user intent.

---

## 3.8 Retrieval Planning

The Retrieval Planner decides **how retrieval should happen**.

It may choose:

```text
Semantic only
Lexical only
Hybrid
Multi-query
Multi-hop
Version-filtered
Metadata-filtered
Hierarchical
Retry-based
```

Example:

```text
Simple definition
→ Hybrid

Exact error message
→ BM25S-heavy

Conceptual explanation
→ Semantic-heavy

Version-specific troubleshooting
→ Metadata filtering + Hybrid

Comparison
→ Separate retrieval branches
```

The planner should not use a single fixed retrieval strategy for every query.

---

## 3.9 Semantic Retrieval

Semantic retrieval uses embeddings to identify conceptually related knowledge.

Conceptual flow:

```text
Query
 ↓
Embedding Model
 ↓
Query Vector
 ↓
Vector Index
 ↓
Candidate Chunks
```

The semantic retriever should support:

- metadata filtering
- software filtering
- version filtering
- expert-specific scope
- configurable candidate count

Qdrant is the initial vector retrieval backend.

---

## 3.10 Lexical Retrieval — BM25S

SIP will use **BM25S** as its lexical retrieval mechanism.

BM25S is particularly useful for software knowledge because exact terminology matters.

Examples:

```text
docker-compose
kubectl
ECONNREFUSED
ERR_MODULE_NOT_FOUND
--network
Dockerfile
useEffect
HTTP 502
```

Semantic embeddings may understand the general concept but can underweight exact tokens.

BM25S provides complementary lexical matching.

Therefore:

```text
Semantic Retrieval
        +
BM25S Retrieval
        ↓
Complementary Candidates
```

---

## 3.11 Metadata Filtering

Retrieval must support structured constraints.

Possible metadata:

```text
software
software_version
document_type
source
source_authority
publication_date
last_updated
language
section
topic
```

Example:

```text
Software = Docker
Version = 27.x
Document Type = Official Documentation
```

Metadata filtering should happen as early as practical to reduce irrelevant candidates.

---

## 3.12 Result Fusion

Semantic and lexical retrieval produce independently ranked result sets.

They must be merged into a unified candidate set.

Conceptually:

```text
Semantic Results
      │
      ├──────────┐
      │          │
      ↓          ↓
             Fusion
      ↑          ↑
      │          │
BM25S Results
```

The initial fusion strategy should use **Reciprocal Rank Fusion (RRF)**.

RRF combines ranking positions rather than directly assuming that raw scores from different retrievers are comparable.

Output:

```text
Unified Candidate Set
```

---

## 3.13 Candidate Deduplication

Different retrieval strategies may return the same chunk.

Therefore duplicate candidates must be removed before reranking.

Deduplication should operate using stable knowledge identifiers rather than only raw text equality.

Example:

```text
Semantic:
Chunk A
Chunk B
Chunk C

BM25S:
Chunk B
Chunk C
Chunk D

After deduplication:

A
B
C
D
```

---

## 3.14 Cross-Encoder Reranking

Initial retrieval is optimized for candidate recall.

Reranking is optimized for candidate relevance.

The Cross-Encoder receives:

```text
Query + Candidate
```

and computes a relevance score.

Conceptually:

```text
Query
  +
Candidate A → Score
Candidate B → Score
Candidate C → Score
Candidate D → Score
```

Candidates are then reordered.

The reranker should operate after candidate fusion.

---

## 3.15 Why Reranking Exists

Embedding similarity answers approximately:

> “Are these texts semantically related?”

The reranker should answer:

> “How relevant is this specific candidate to this specific query?”

This distinction is critical for technical retrieval.

---

## 3.16 Context Optimization

The reranked candidates must not automatically all be sent to the LLM.

The Context Optimizer performs:

### Relevance Filtering

Remove low-value candidates.

### Deduplication

Remove repeated information.

### Compression

Reduce unnecessary text when appropriate.

### Ordering

Arrange evidence to improve comprehension.

### Token Budgeting

Keep context within the configured budget.

Conceptual flow:

```text
Reranked Candidates
       ↓
Relevance Filter
       ↓
Duplicate Removal
       ↓
Compression
       ↓
Ordering
       ↓
Token Budget
       ↓
Final Context
```

---

## 3.17 Evidence Packaging

The final retrieval result should not be just a list of text strings.

Each evidence item should retain provenance.

Conceptually:

```text
Evidence
├── evidence_id
├── chunk_id
├── document_id
├── document_version
├── source
├── title
├── section
├── text
├── retrieval_score
├── rerank_score
└── metadata
```

This allows:

```text
Answer
 ↓
Citation
 ↓
Evidence
 ↓
Chunk
 ↓
Document
 ↓
Source
```

---

## 3.18 Evidence Evaluation

The Evidence Evaluator determines whether the current evidence is adequate.

Evaluation dimensions may include:

- relevance
- coverage
- consistency
- version compatibility
- source authority
- redundancy
- completeness

Possible result:

```text
Evidence Status:
SUFFICIENT
```

or:

```text
Evidence Status:
INSUFFICIENT
```

or:

```text
Evidence Status:
CONTRADICTORY
```

---

## 3.19 Evidence Sufficiency Gate

This is one of the core differences from conventional RAG.

```text
                    Evidence
                       ↓
                Sufficiency Gate
                 /           \
               YES            NO
                ↓              ↓
          Generate         Retry
```

The gate should prevent unsupported generation.

---

## 3.20 Retrieval Retry

When evidence is insufficient, the engine may perform another retrieval iteration.

Possible retry actions:

```text
Query Rewrite
Query Expansion
Different Retrieval Strategy
Broader Candidate Set
Different Metadata Scope
Additional Source Type
Sub-question Retrieval
```

Example:

```text
Attempt 1
Hybrid Retrieval
      ↓
Insufficient
      ↓
Attempt 2
Expanded Query
      ↓
Insufficient
      ↓
Attempt 3
Broader Version Scope
      ↓
Evidence Found
```

The number of retries must be bounded.

---

## 3.21 Query Decomposition

Complex questions may be decomposed into independent retrieval tasks.

Example:

```text
"Compare Docker networking in version X and Y
and explain why my application behaves differently."
```

Possible decomposition:

```text
Q1 → Networking behavior in X
Q2 → Networking behavior in Y
Q3 → Changes between X and Y
Q4 → Relationship to observed behavior
```

Each sub-query can have its own retrieval process.

The resulting evidence is then combined.

---

## 3.22 Multi-Hop Retrieval

Some questions require evidence from multiple documents.

```text
Query
 ↓
Evidence A
 ↓
Intermediate Finding
 ↓
Evidence B
 ↓
Combined Evidence
 ↓
Answer
```

The engine must preserve provenance for every hop.

---

## 3.23 Version-Aware Retrieval

Version information must influence retrieval.

Example:

```text
User:
"How do I configure feature X in Docker 27?"
```

The retrieval planner should prioritize:

```text
Docker
+
Version 27
+
Feature X
```

rather than retrieving generic Docker information first.

If the required version-specific evidence is unavailable, the system should explicitly expose that limitation.

---

## 3.24 Source Authority

Different sources have different evidentiary value.

The retrieval system should preserve source classification.

Example:

```text
Official Documentation
Release Notes
GitHub Repository
Issue Tracker
Community Discussion
Blog
```

Authority should be represented as metadata.

The system should not blindly treat every retrieved source as equivalent.

---

## 3.25 Contradictory Evidence

Multiple sources may disagree.

The engine must not silently merge contradictory claims.

Conceptual flow:

```text
Evidence A
     +
Evidence B
     ↓
Conflict Detection
     ↓
Contradiction
     ↓
Generation receives both
     +
Source metadata
```

The final answer should distinguish the conflict rather than inventing a unified conclusion.

---

## 3.26 Generation Interface

The Adaptive RAG Engine returns a structured result to the generation layer.

Conceptually:

```python
RetrievalResult(
    query=...,
    evidence=[...],
    context=...,
    evidence_status=...,
    citations=[...],
    metadata=...
)
```

The generation layer must not need to understand how the evidence was retrieved.

---

## 3.27 Retrieval Metadata

Every retrieval run should record enough information for debugging and evaluation.

Minimum conceptual metadata:

```text
retrieval_run_id
query
expert_id
software
software_version
query_type
retrieval_strategy
semantic_candidate_count
lexical_candidate_count
fused_candidate_count
reranked_candidate_count
final_evidence_count
retry_count
latency
evidence_status
```

---

## 3.28 Caching

Caching may be applied at multiple levels.

Possible cache targets:

- query analysis
- query transformation
- embeddings
- retrieval results
- reranking results
- frequently accessed knowledge

Caching must respect:

- software version
- knowledge version
- expert configuration
- retrieval configuration

A stale cache must not silently produce outdated software guidance.

---

## 3.29 Latency Budget

Adaptive retrieval introduces additional processing stages.

Therefore the engine must explicitly track latency.

Conceptual budget:

```text
Query Analysis
      +
Transformation
      +
Retrieval
      +
Fusion
      +
Reranking
      +
Context Optimization
      +
Generation
```

The implementation should measure each stage independently before optimizing it.

Premature optimization is prohibited.

---

## 3.30 Failure Handling

### Embedding Failure

Fallback or retry according to configured policy.

### BM25S Failure

Semantic retrieval may continue if the system policy permits.

### Vector Database Failure

Return controlled retrieval failure rather than hallucinating.

### Reranker Failure

Use configured fallback ranking strategy.

### LLM Failure

Handled by the LLM Gateway, not the retrieval subsystem.

### Knowledge Unavailable

Return explicit evidence-unavailable state.

---

## 3.31 Retrieval Pipeline Contract

The Adaptive RAG Engine accepts:

```text
Query
Expert Context
Conversation Context
Software Identity
Version Context
Retrieval Policy
```

and produces:

```text
Evidence
Optimized Context
Citations
Evidence Status
Retrieval Metadata
```

Therefore:

```text
INPUT
  ↓
Adaptive RAG
  ↓
OUTPUT
```

The internals can evolve without changing the external contract.

---

## 3.32 Initial Retrieval Configuration

The first implementation should use:

```text
Semantic Retrieval
        +
BM25S
        ↓
RRF
        ↓
Cross-Encoder
        ↓
Context Optimization
        ↓
Evidence Gate
```

This is the **baseline adaptive pipeline**.

More advanced strategies should be introduced only after benchmarking the baseline.

---

## 3.33 Traditional RAG Baseline

Before proving SIP's Adaptive RAG improvements, implement a controlled conventional RAG baseline.

```text
Query
 ↓
Embedding
 ↓
Vector Search
 ↓
Top-K
 ↓
LLM
```

This baseline is essential.

Without it, claims such as:

> “Adaptive RAG is better”

cannot be experimentally supported.

---

## 3.34 Experimental Comparison

The evaluation framework should eventually compare:

```text
Traditional RAG
       VS
SIP Adaptive RAG
```

using the same:

- dataset
- documents
- questions
- LLM
- embedding model
- evaluation methodology

Possible metrics:

| Category    | Metric                 |
| ----------- | ---------------------- |
| Retrieval   | Recall@K               |
| Retrieval   | Precision@K            |
| Retrieval   | MRR                    |
| Retrieval   | NDCG                   |
| Context     | Relevance              |
| Context     | Coverage               |
| Generation  | Faithfulness           |
| Generation  | Answer correctness     |
| Reliability | Abstention quality     |
| Performance | Latency                |
| Efficiency  | Token usage            |
| System      | Retrieval failure rate |

Actual evaluation implementation belongs to Phase 9.

---

## 3.35 Adaptive RAG State Machine

The retrieval lifecycle can be represented as:

```text
START
  ↓
ANALYZE
  ↓
CLASSIFY
  ↓
TRANSFORM
  ↓
PLAN
  ↓
RETRIEVE
  ↓
FUSE
  ↓
RERANK
  ↓
OPTIMIZE
  ↓
EVALUATE
  │
  ├── SUFFICIENT ───────→ GENERATE
  │
  ├── RETRY ────────────→ TRANSFORM / PLAN
  │
  └── ABSTAIN ──────────→ NO-SUFFICIENT-EVIDENCE
```

Every transition should be observable.

---

## 3.36 Implementation Module Structure

Recommended Python structure:

```text
adaptive_rag/
│
├── analyzer/
│   ├── query_analyzer.py
│   └── query_classifier.py
│
├── transformer/
│   ├── rewriter.py
│   ├── expander.py
│   └── decomposer.py
│
├── planner/
│   └── retrieval_planner.py
│
├── retrieval/
│   ├── semantic.py
│   ├── bm25s.py
│   └── metadata.py
│
├── fusion/
│   └── rrf.py
│
├── reranking/
│   └── cross_encoder.py
│
├── context/
│   ├── optimizer.py
│   ├── compressor.py
│   └── deduplicator.py
│
├── evidence/
│   ├── evaluator.py
│   ├── sufficiency.py
│   └── provenance.py
│
├── retry/
│   └── strategy.py
│
├── pipeline/
│   └── orchestrator.py
│
├── models/
│   ├── query.py
│   ├── evidence.py
│   └── retrieval_result.py
│
└── config/
    └── settings.py
```

This is a **logical implementation structure**, not a requirement to freeze every filename before development.

---

## 3.37 Testing Strategy

Each stage must be independently testable.

### Unit Tests

- query classification
- transformation
- BM25S retrieval
- metadata filtering
- RRF
- deduplication
- reranking
- evidence scoring
- sufficiency decisions

### Integration Tests

```text
Query
 ↓
Retrieval
 ↓
Fusion
 ↓
Reranking
 ↓
Evidence
```

### End-to-End Tests

```text
User Query
 ↓
Adaptive RAG
 ↓
LLM
 ↓
Grounded Answer
```

### Regression Tests

Known queries and expected evidence should be stored so retrieval changes can be measured.

---

## 3.38 Security Considerations

The RAG engine must respect Expert and authorization boundaries.

It must not retrieve knowledge outside the permitted expert scope.

Conceptually:

```text
User
 ↓
Expert
 ↓
Knowledge Scope
 ↓
Retrieval
```

Not:

```text
User
 ↓
Global Knowledge
```

This prevents cross-expert knowledge leakage.

---

## 3.39 What Phase 3 Does NOT Own

The Adaptive RAG Engine does **not** own:

- web crawling
- source discovery
- document downloading
- document parsing
- canonical document storage
- PostgreSQL schema
- expert lifecycle
- desktop UI
- LLM provider implementation
- software tool execution
- enterprise deployment

Those belong to later phases.

---

## 3.40 Phase 2 → Phase 3 Contract

Phase 2 established:

```text
Expert
   ↓
Adaptive RAG
   ↓
Evidence
   ↓
LLM Gateway
```

Phase 3 now defines the internals:

```text
Adaptive RAG
│
├── Analyze
├── Classify
├── Transform
├── Plan
├── Retrieve
│   ├── Semantic
│   └── BM25S
├── Fuse
├── Rerank
├── Optimize
├── Evaluate
├── Retry
└── Abstain
```

No contradiction exists between the two phases.

---

## 3.41 Phase 3 → Phase 4 Contract

Phase 3 requires structured knowledge entities but does not define their storage schema.

It expects access to:

```text
Document
DocumentVersion
Chunk
Metadata
Embedding
Source
```

Phase 4 will define:

- PostgreSQL schema
- Qdrant payload structure
- identifiers
- indexes
- relationships
- version representation
- provenance representation
- storage lifecycle

---

## 3.42 Phase 3 → Phase 5 Contract

Phase 3 consumes processed knowledge.

Phase 5 will provide:

```text
External Source
 ↓
Acquisition
 ↓
Parsing
 ↓
Normalization
 ↓
Chunking
 ↓
Metadata
 ↓
Embedding
 ↓
Index
```

Phase 3 should never directly crawl the internet.

---

## 3.43 Phase 3 Completion Criteria

Phase 3 is complete when:

- [x] Adaptive retrieval architecture defined
- [x] Query analysis defined
- [x] Query classification defined
- [x] Query transformation defined
- [x] Retrieval planning defined
- [x] Semantic retrieval defined
- [x] **BM25S lexical retrieval locked**
- [x] Metadata filtering defined
- [x] RRF fusion defined
- [x] Candidate deduplication defined
- [x] Cross-encoder reranking defined
- [x] Context optimization defined
- [x] Evidence packaging defined
- [x] Evidence evaluation defined
- [x] Sufficiency gate defined
- [x] Retry strategy defined
- [x] Abstention defined
- [x] Version-aware retrieval defined
- [x] Contradictory evidence handling defined
- [x] Provenance/citation flow defined
- [x] Caching considerations defined
- [x] Failure boundaries defined
- [x] Traditional RAG baseline defined
- [x] Evaluation boundary defined
- [x] Phase 3 → Phase 4 contract defined
- [x] Phase 3 → Phase 5 contract defined

---

## 3.44 Final Adaptive RAG Architecture

```text
                         USER QUERY
                              │
                              ▼
                    ┌──────────────────┐
                    │  QUERY ANALYZER  │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │ QUERY CLASSIFIER │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │ QUERY TRANSFORM  │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │ RETRIEVAL PLAN   │
                    └────────┬─────────┘
                             ↓
                ┌────────────┴────────────┐
                ↓                         ↓
       ┌────────────────┐        ┌────────────────┐
       │ Semantic Search│        │     BM25S      │
       │    Qdrant      │        │    Search      │
       └───────┬────────┘        └───────┬────────┘
               │                         │
               └───────────┬─────────────┘
                           ↓
                  ┌──────────────────┐
                  │    RRF FUSION    │
                  └────────┬─────────┘
                           ↓
                  ┌──────────────────┐
                  │   DEDUPLICATION  │
                  └────────┬─────────┘
                           ↓
                  ┌──────────────────┐
                  │ CROSS-ENCODER    │
                  │    RERANKER      │
                  └────────┬─────────┘
                           ↓
                  ┌──────────────────┐
                  │ CONTEXT OPTIMIZER│
                  └────────┬─────────┘
                           ↓
                  ┌──────────────────┐
                  │ EVIDENCE EVAL    │
                  └────────┬─────────┘
                           ↓
                     ┌─────┴─────┐
                     │ SUFFICIENT│
                     └─────┬─────┘
                       YES │ NO
                           │
              ┌────────────┴───────────┐
              ↓                        ↓
        ┌─────────────┐       ┌────────────────┐
        │ LLM Gateway │       │ RETRY /        │
        │  Generation │       │ REFORMULATION  │
        └──────┬──────┘       └───────┬────────┘
               ↓                      │
        ┌─────────────┐               │
        │ VALIDATION  │◄──────────────┘
        └──────┬──────┘
               ↓
       ANSWER + CITATIONS
```

## Phase 3 ka locked core

```text
Traditional RAG
────────────────────────────
Retrieve → Generate


SIP Adaptive RAG
────────────────────────────
Analyze
   ↓
Classify
   ↓
Transform
   ↓
Plan
   ↓
Semantic + BM25S
   ↓
RRF
   ↓
Rerank
   ↓
Optimize
   ↓
Evaluate Evidence
   ↓
Retry / Abstain
   ↓
Generate
   ↓
Validate
```
