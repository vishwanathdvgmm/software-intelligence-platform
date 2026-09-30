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
║  PHASE 4  → Data Layer & Knowledge Storage - Completed     ║
║  PHASE 5  → Knowledge Ingestion & Crawling - Completed     ║
║  PHASE 6  → Expert System & Expert Lifecycle - In Progress ║
║  PHASE 7  → LLM Gateway, Tools & Agent Runtime             ║
║  PHASE 8  → Desktop Application Architecture               ║
║  PHASE 9  → Evaluation, Benchmarking & Observability       ║
║  PHASE 10 → Security, Deployment & Enterprise              ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
```

> **Project:** Software Intelligence Platform
>
> **Phase:** 6
>
> **Subsystem:** Expert System & Expert Lifecycle
>
> **Status:** Implementation Specification

---

## 6.1 Phase Objective

SIP ka objective sirf ek global knowledge base banana nahi hai.

SIP ko multiple specialized **Experts** support karne chahiye.

Example:

```text
SIP
│
├── Python Expert
├── Docker Expert
├── PostgreSQL Expert
├── FastAPI Expert
├── Rust Expert
└── Kubernetes Expert
```

Har Expert ke paas ho sakta hai:

- apna domain
- apna knowledge scope
- apne sources
- software/version information
- retrieval configuration
- system behavior
- evaluation profile
- lifecycle state

Therefore:

```text
Expert
   ↓
Knowledge Scope
   ↓
Retrieval Configuration
   ↓
Reasoning Configuration
   ↓
Evaluation
```

---

## 6.2 Core Concept

Traditional RAG:

```text
One Knowledge Base
        ↓
One Retriever
        ↓
One LLM
```

SIP:

```text
                    SIP
                     │
        ┌────────────┼────────────┐
        ↓            ↓            ↓
     Expert A     Expert B     Expert C
        │            │            │
      Python       Docker      PostgreSQL
        │            │            │
     Knowledge    Knowledge    Knowledge
        │            │            │
     Retrieval    Retrieval    Retrieval
```

Expert therefore acts as a **domain intelligence boundary**.

---

## 6.3 What Is an Expert?

An Expert is a logical SIP entity representing a specialized knowledge and reasoning domain.

Example:

```text
Expert:
    name = Python Expert
    domain = Python
    scope = Python ecosystem
    status = ACTIVE
```

An Expert is **not** merely:

```text
Expert = LLM
```

Instead:

```text
Expert =
    Domain Definition
    +
    Knowledge Scope
    +
    Source Configuration
    +
    Retrieval Configuration
    +
    Behavioral Configuration
    +
    Evaluation Configuration
```

---

## 6.4 Expert Responsibilities

Phase 6 owns:

- Expert creation
- Expert configuration
- Expert identity
- domain definition
- knowledge scope
- source association
- Expert lifecycle
- Expert versioning
- Expert activation/deactivation
- configuration management
- Expert health
- Expert readiness
- Expert-level evaluation metadata
- Expert dependency management

---

## 6.5 What Phase 6 Does NOT Own

Phase 6 does not implement:

- document crawling
- web scraping
- raw artifact acquisition
- vector database implementation
- BM25S implementation
- embedding generation
- cross-encoder implementation
- query execution
- final answer generation

Those belong to other phases.

Conceptually:

```text
Phase 5
→ Knowledge Acquisition

Phase 4
→ Knowledge Storage

Phase 6
→ Expert Management

Later Retrieval/Runtime phases
→ Expert Execution
```

---

## 6.6 Expert Identity

Every Expert requires a stable identity.

Minimum conceptual fields:

```text
expert_id
name
slug
description
domain
status
created_at
updated_at
```

Example:

```text
expert_id:
exp_python

name:
Python Expert

slug:
python

domain:
Python Programming
```

`expert_id` should remain stable throughout the Expert's lifecycle.

---

## 6.7 Expert Scope

An Expert must have an explicit scope.

Example:

```text
Python Expert
```

may cover:

```text
Python language
Python standard library
Python packaging
Python ecosystem
Python frameworks
```

But it should not automatically mean:

```text
All programming knowledge
```

Scope boundaries are necessary to maintain retrieval precision.

---

## 6.8 Expert Knowledge Boundary

An Expert should be associated with explicit knowledge.

Conceptually:

```text
Expert
  ↓
Knowledge Scope
  ↓
Documents
  ↓
Document Versions
  ↓
Chunks
```

The Expert should not arbitrarily search the entire global knowledge corpus unless explicitly configured.

---

## 6.9 Expert → Source Association

An Expert can have multiple sources.

Example:

```text
Python Expert
│
├── Python Official Documentation
├── Python PEPs
├── Python GitHub Repository
├── Python Release Notes
└── Selected Community Sources
```

Source association should be explicit.

---

## 6.10 Source Authority Metadata

Sources associated with an Expert should retain source metadata such as:

```text
source_type
authority_level
trust_metadata
freshness
software_version
```

Important:

> Source authority is metadata; it is not proof that every statement from that source is correct.

---

## 6.11 Expert Configuration

An Expert should have a configuration object.

Conceptually:

```text
ExpertConfig
│
├── knowledge_scope
├── retrieval_config
├── generation_config
├── evidence_config
├── version_policy
└── evaluation_config
```

This allows Experts to behave differently without creating separate codebases.

---

## 6.12 Retrieval Configuration

An Expert may define retrieval preferences.

Example:

```text
retrieval_config:
    semantic_enabled = true
    lexical_enabled = true
    reranking_enabled = true
```

The underlying retrieval implementation belongs to the retrieval subsystem.

Phase 6 only defines the Expert's configuration contract.

---

## 6.13 Evidence Configuration

An Expert can define evidence requirements.

Example:

```text
evidence_config:
    require_sources = true
    minimum_evidence = configured
    allow_insufficient_evidence = false
```

The actual evidence evaluation occurs downstream.

---

## 6.14 Generation Configuration

The Expert can define generation-level behavior.

Conceptually:

```text
generation_config:
    model
    temperature
    max_tokens
    citation_mode
```

These values should be configuration, not hard-coded application logic.

---

## 6.15 Version Awareness

Software knowledge is time-sensitive.

For example:

```text
Python 3.10
Python 3.11
Python 3.12
Python 3.13
```

An Expert may therefore need:

```text
software
software_version
version_policy
```

Example:

```text
Python Expert
    ↓
Target Version: 3.13
```

---

## 6.16 Version Policy

Possible policies:

```text
LATEST
SPECIFIC_VERSION
VERSION_RANGE
ALL_SUPPORTED
```

Example:

```text
Python Expert
version_policy = LATEST
```

or:

```text
FastAPI Expert
version_policy = SPECIFIC_VERSION
version = 0.116
```

The exact supported version semantics should be finalized during implementation.

---

## 6.17 Expert Lifecycle

An Expert must have a defined lifecycle.

Recommended state model:

```text
DRAFT
  ↓
CONFIGURING
  ↓
BUILDING
  ↓
VALIDATING
  ↓
READY
  ↓
ACTIVE
  ↓
UPDATING
  ↓
ACTIVE
```

Terminal/deactivation paths:

```text
ACTIVE
  ↓
DISABLED
```

or:

```text
ACTIVE
  ↓
ARCHIVED
```

---

## 6.18 DRAFT

Initial state.

```text
DRAFT
```

The Expert exists but is not operational.

Possible actions:

- configure metadata
- define domain
- configure sources
- define version policy

---

## 6.19 CONFIGURING

Configuration is being prepared.

```text
CONFIGURING
```

The Expert may still be incomplete.

It must not become queryable as a production Expert.

---

## 6.20 BUILDING

The Expert's knowledge environment is being constructed.

Example:

```text
BUILDING
   ↓
Knowledge acquisition
   ↓
Processing
   ↓
Index preparation
```

This state represents system construction rather than user interaction.

---

## 6.21 VALIDATING

The Expert has been built but requires validation.

Validation may include:

```text
Knowledge availability
Source health
Retrieval health
Configuration validation
Evaluation checks
```

---

## 6.22 READY

The Expert has passed structural validation.

```text
READY
```

means:

> The Expert can be activated, but is not necessarily serving queries yet.

---

## 6.23 ACTIVE

Only an `ACTIVE` Expert should normally serve production queries.

```text
ACTIVE
```

means:

```text
Expert
+
Required Knowledge
+
Required Configuration
+
Required Dependencies
```

are operational.

---

## 6.24 UPDATING

When an active Expert receives significant configuration or knowledge updates:

```text
ACTIVE
   ↓
UPDATING
```

The update process should avoid exposing partially updated state.

After successful validation:

```text
UPDATING
   ↓
VALIDATING
   ↓
ACTIVE
```

---

## 6.25 DISABLED

An Expert can be temporarily disabled.

```text
ACTIVE
   ↓
DISABLED
```

No normal queries should be routed to a disabled Expert.

---

## 6.26 ARCHIVED

An Expert that is no longer maintained can be archived.

```text
ACTIVE
   ↓
ARCHIVED
```

Archived Experts should remain historically identifiable rather than being physically deleted by default.

---

## 6.27 State Transition Rules

State transitions must be explicit.

Example:

```text
DRAFT
  → CONFIGURING

CONFIGURING
  → BUILDING

BUILDING
  → VALIDATING

VALIDATING
  → READY
  → CONFIGURING

READY
  → ACTIVE
  → CONFIGURING

ACTIVE
  → UPDATING
  → DISABLED
  → ARCHIVED

UPDATING
  → VALIDATING
  → ACTIVE
```

Invalid transitions must be rejected.

---

## 6.28 Expert Versioning

Expert configuration itself should be versioned.

Example:

```text
Python Expert
│
├── Configuration v1
├── Configuration v2
└── Configuration v3
```

This enables reproducibility.

A historical query should be able to identify which Expert configuration was active.

---

## 6.29 Expert Snapshot

An Expert version should conceptually represent a snapshot:

```text
ExpertSnapshot
│
├── expert_version
├── configuration
├── knowledge_scope
├── source_set
├── software_version_policy
└── retrieval configuration
```

This becomes important for evaluation.

---

## 6.30 Expert and Knowledge Versioning

Two different things must not be confused:

```text
Knowledge Version
```

vs.

```text
Expert Version
```

Example:

```text
Python Documentation
→ Document v8

Python Expert
→ Expert Config v3
```

They are independent version dimensions.

---

## 6.31 Expert Dependencies

An Expert may depend on:

```text
Knowledge
Sources
Indexes
Embedding model
Reranker
LLM
Configuration
```

These dependencies should be represented explicitly.

---

## 6.32 Dependency Graph

Conceptually:

```text
Python Expert
     │
     ├── Python Knowledge
     │       ├── Documents
     │       └── Indexes
     │
     ├── Embedding Model
     │
     ├── Reranker
     │
     └── LLM
```

This enables readiness checks.

---

## 6.33 Expert Readiness

An Expert should not become `ACTIVE` merely because its metadata exists.

Readiness should verify:

```text
Expert configuration ✓
Knowledge available ✓
Required indexes ✓
Required models ✓
Source state acceptable ✓
Configuration valid ✓
Evaluation requirements ✓
```

Only then:

```text
READY → ACTIVE
```

---

## 6.34 Health Model

Expert health should be observable.

Possible health dimensions:

```text
KNOWLEDGE_HEALTH
SOURCE_HEALTH
INDEX_HEALTH
MODEL_HEALTH
CONFIGURATION_HEALTH
RETRIEVAL_HEALTH
```

Overall health should not hide the individual dimensions.

---

## 6.35 Health vs State

These are different concepts.

Example:

```text
State:
ACTIVE

Health:
DEGRADED
```

An Expert may remain active while one non-critical source is temporarily unavailable.

Therefore:

```text
Lifecycle State ≠ Operational Health
```

---

## 6.36 Expert Health States

Possible health:

```text
HEALTHY
DEGRADED
UNHEALTHY
UNKNOWN
```

Example:

```text
Python Expert
State: ACTIVE
Health: DEGRADED

Reason:
GitHub source unavailable
```

---

## 6.37 Expert Creation Workflow

Creation:

```text
Create Expert
      ↓
DRAFT
      ↓
Configure Domain
      ↓
Configure Sources
      ↓
Configure Version Policy
      ↓
Configure Runtime
      ↓
Validate Configuration
```

---

## 6.38 Expert Build Workflow

```text
Configuration
     ↓
BUILDING
     ↓
Acquire Knowledge
     ↓
Process Knowledge
     ↓
Build Indexes
     ↓
Validate
     ↓
READY
```

Phase 5 handles acquisition.

Later processing/indexing phases handle the corresponding downstream operations.

---

## 6.39 Expert Activation

Activation should be an explicit lifecycle operation.

```text
READY
  ↓
Activation Validation
  ↓
ACTIVE
```

Activation should fail if mandatory dependencies are missing.

---

## 6.40 Expert Deactivation

```text
ACTIVE
  ↓
Disable
  ↓
DISABLED
```

Disabling should not delete knowledge.

---

## 6.41 Expert Update

Configuration update:

```text
ACTIVE
  ↓
Create New Configuration Version
  ↓
Validate
  ↓
Build/Prepare
  ↓
Activate New Version
```

The old version should remain traceable.

---

## 6.42 Atomic Activation

A critical rule:

> A partially built Expert configuration must never become the active configuration.

Therefore:

```text
Old Version
     ↓
New Version
     ↓
Validate
     ↓
Ready
     ↓
Atomic Activation
```

This avoids inconsistent runtime behavior.

---

## 6.43 Expert Deletion

Physical deletion should not be the default.

Prefer:

```text
ARCHIVED
```

because historical references may depend on the Expert.

---

## 6.44 Expert Registry

SIP should maintain an Expert Registry.

Conceptually:

```text
Expert Registry
│
├── Python Expert
├── Docker Expert
├── PostgreSQL Expert
└── FastAPI Expert
```

Registry responsibilities:

- discover Experts
- retrieve metadata
- lifecycle operations
- state tracking
- health information
- version information

---

## 6.45 Expert Resolution

When the user asks a question, the system eventually needs to determine:

```text
Which Expert should handle this?
```

Example:

```text
"How do I create an async endpoint in FastAPI?"
                    ↓
             FastAPI Expert
```

However, **Expert selection itself should not be hard-coded into Phase 6**.

Phase 6 exposes Expert metadata and contracts.

The runtime/query orchestration layer decides which Expert is appropriate.

---

## 6.46 Multi-Expert Queries

Some questions may require multiple Experts.

Example:

> "How can I deploy a FastAPI application using Docker and PostgreSQL?"

Potential Experts:

```text
FastAPI Expert
Docker Expert
PostgreSQL Expert
```

Conceptually:

```text
User Query
    ↓
Expert Resolution
    ↓
┌───────────┬───────────┬────────────┐
FastAPI     Docker      PostgreSQL
Expert      Expert      Expert
    └───────────┬───────────┘
                ↓
         Evidence Fusion
```

Multi-Expert orchestration belongs to the runtime layer, not Expert lifecycle management.

---

## 6.47 Expert Isolation

An Expert should have logical boundaries.

For example:

```text
Python Expert
```

should not accidentally retrieve:

```text
Unrelated Medical Knowledge
```

unless explicitly configured.

This supports precision and reduces cross-domain contamination.

---

## 6.48 Shared Knowledge

Not all knowledge needs to be duplicated.

Example:

```text
Common Programming Concepts
```

could potentially be shared across:

```text
Python Expert
Rust Expert
Go Expert
```

Therefore the architecture should support:

```text
Shared Knowledge
       ↓
Multiple Experts
```

without duplicating physical documents.

---

## 6.49 Expert Knowledge Mapping

Conceptually:

```text
Expert
  ↓
Knowledge Scope Mapping
  ↓
Knowledge IDs
```

The mapping layer determines which knowledge belongs to which Expert.

---

## 6.50 Expert Policies

Each Expert may have policies.

Example:

```text
ExpertPolicy
│
├── source_policy
├── freshness_policy
├── version_policy
├── evidence_policy
└── answer_policy
```

This keeps domain-specific behavior configurable.

---

## 6.51 Freshness Policy

Example:

```text
Python Expert
freshness:
    prefer_recent = true
```

Another historical Expert could use:

```text
freshness:
    historical_snapshot = required
```

Exact policy semantics will be defined during runtime design.

---

## 6.52 Evaluation Profile

Each Expert should have an evaluation profile.

Example:

```text
Python Expert
│
├── Retrieval evaluation
├── Groundedness evaluation
├── Answer accuracy
└── Citation quality
```

This connects Expert lifecycle with the evaluation subsystem.

---

## 6.53 Expert Readiness Gate

Before activation:

```text
                 EXPERT
                    ↓
          Configuration Valid?
              /          \
            NO            YES
            ↓              ↓
          STOP        Knowledge Ready?
                         /      \
                       NO        YES
                       ↓          ↓
                     STOP     Dependencies?
                                  / \
                                NO   YES
                                ↓     ↓
                              STOP   VALIDATE
                                          ↓
                                        ACTIVE
```

---

## 6.54 Expert Lifecycle Events

Important events should be emitted.

Examples:

```text
EXPERT_CREATED
EXPERT_CONFIG_UPDATED
EXPERT_BUILD_STARTED
EXPERT_BUILD_COMPLETED
EXPERT_VALIDATION_STARTED
EXPERT_VALIDATION_FAILED
EXPERT_ACTIVATED
EXPERT_DISABLED
EXPERT_ARCHIVED
EXPERT_HEALTH_CHANGED
```

These events can later support observability and auditing.

---

## 6.55 Auditability

Lifecycle operations should be auditable.

Record:

```text
event
expert_id
expert_version
timestamp
actor/system
previous_state
new_state
reason
```

This answers:

> "Why is this Expert currently active?"

---

## 6.56 Expert API Boundary

Phase 6 should expose an internal service/API contract.

Conceptually:

```text
POST   /experts
GET    /experts
GET    /experts/{id}
PATCH  /experts/{id}
POST   /experts/{id}/build
POST   /experts/{id}/validate
POST   /experts/{id}/activate
POST   /experts/{id}/disable
POST   /experts/{id}/archive
GET    /experts/{id}/health
GET    /experts/{id}/versions
```

Exact external API design can be finalized later.

---

## 6.57 Expert Domain Model

Conceptually:

```text
Expert
│
├── Identity
│
├── Domain
│
├── Scope
│
├── Sources
│
├── Knowledge Mapping
│
├── Configuration
│
├── Version
│
├── Dependencies
│
├── Lifecycle State
│
├── Health
│
└── Evaluation Profile
```

---

## 6.58 Suggested Internal Structure

```text
experts/
│
├── domain/
│   ├── expert.py
│   ├── expert_version.py
│   ├── expert_state.py
│   ├── expert_health.py
│   └── policies.py
│
├── lifecycle/
│   ├── manager.py
│   ├── transitions.py
│   ├── activation.py
│   └── validation.py
│
├── registry/
│   ├── registry.py
│   └── resolver.py
│
├── configuration/
│   ├── config.py
│   ├── retrieval.py
│   ├── generation.py
│   └── evidence.py
│
├── dependencies/
│   ├── checker.py
│   └── readiness.py
│
├── health/
│   ├── checker.py
│   └── models.py
│
└── events/
    ├── events.py
    └── publisher.py
```

---

## 6.59 Expert Lifecycle — Complete Flow

```text
                    CREATE
                      ↓
                    DRAFT
                      ↓
                 CONFIGURING
                      ↓
                  BUILDING
                      ↓
                 VALIDATING
                 /         \
              FAIL          PASS
               ↓              ↓
         CONFIGURING        READY
                               ↓
                            ACTIVE
                         /     |      \
                        ↓      ↓       ↓
                    UPDATING DISABLED ARCHIVED
                        ↓
                    VALIDATING
                        ↓
                      ACTIVE
```

---

## 6.60 Failure Handling

If build fails:

```text
BUILDING
   ↓
FAIL
   ↓
CONFIGURING / FAILED
```

If validation fails:

```text
VALIDATING
   ↓
FAILED
   ↓
CONFIGURING
```

If activation fails:

```text
READY
   ↓
Activation Failed
   ↓
READY
```

The system must not silently activate a failed Expert.

---

## 6.61 Idempotency

Lifecycle operations should be idempotent where appropriate.

Example:

```text
disable(expert_id)
```

called twice should not create two different states.

Likewise:

```text
activate(version)
```

should not create duplicate activation records.

---

## 6.62 Concurrency Control

Two processes must not simultaneously activate conflicting Expert versions.

Example:

```text
Process A → Activate v4
Process B → Activate v5
```

The lifecycle manager must enforce a consistent final state.

This becomes important once background workers are introduced.

---

## 6.63 Phase 6 → Phase 4 Contract

Phase 6 depends on Phase 4 for persistence of:

```text
Expert
ExpertVersion
ExpertSourceMapping
ExpertKnowledgeMapping
ExpertState
ExpertHealth
LifecycleEvent
```

Phase 4 remains responsible for storage implementation.

---

## 6.64 Phase 6 → Phase 5 Contract

Phase 6 can request knowledge acquisition for an Expert.

Conceptually:

```text
Expert
  ↓
Configured Sources
  ↓
Phase 5
  ↓
Knowledge Acquisition
```

Phase 6 should not implement crawling itself.

---

## 6.65 Phase 6 → Retrieval Runtime Contract

The runtime can ask:

```text
Get active Expert configuration
```

and receive:

```text
ExpertSnapshot
```

Example:

```text
ExpertSnapshot
├── expert_id
├── version
├── domain
├── knowledge_scope
├── retrieval_config
├── evidence_config
├── generation_config
└── version_policy
```

This snapshot becomes the runtime contract.

---

## 6.66 Phase 6 → Evaluation Contract

Evaluation should be able to evaluate an Expert version:

```text
Expert
   ↓
Expert Version
   ↓
Evaluation Dataset
   ↓
Retrieval / Generation
   ↓
Metrics
```

This makes Expert improvements measurable.

---

## 6.67 Expert Lifecycle and Reproducibility

A query result should eventually be traceable to:

```text
Expert ID
Expert Version
Knowledge Version
Retrieval Configuration
Model Version
```

This is critical for debugging.

Example:

```text
Query
 ↓
Python Expert v7
 ↓
Python Docs Snapshot v42
 ↓
Embedding Model X
 ↓
Reranker Y
 ↓
LLM Z
```

Now the result is reproducible.

---

## 6.68 Implementation Priority

Implement Phase 6 in this order:

```text
1. Expert domain model
        ↓
2. Expert configuration model
        ↓
3. Lifecycle state machine
        ↓
4. Expert registry
        ↓
5. Expert versioning
        ↓
6. Knowledge/source mapping
        ↓
7. Dependency model
        ↓
8. Readiness checks
        ↓
9. Health model
        ↓
10. Lifecycle events
        ↓
11. Expert API/service
        ↓
12. Evaluation integration
        ↓
13. Multi-Expert support
```

Multi-Expert support can initially remain a contract even if the first MVP operates with one active Expert.

---

## 6.69 MVP Scope

For the first working implementation, support:

```text
✓ Create Expert
✓ Configure Expert
✓ Define domain
✓ Associate knowledge
✓ Associate sources
✓ Expert version
✓ Lifecycle states
✓ Build
✓ Validate
✓ Activate
✓ Disable
✓ Archive
✓ Health
✓ Basic readiness checks
✓ Audit events
```

Defer:

```text
→ sophisticated multi-agent behavior
→ automatic Expert creation
→ complex Expert collaboration
→ autonomous configuration optimization
```

Those should not be introduced until the core lifecycle is stable.

---

## 6.70 Testing Strategy

### Unit Tests

Test:

- state transitions
- invalid transitions
- configuration validation
- readiness checks
- version creation
- dependency checks
- health calculation

### Integration Tests

Test:

```text
Expert
 ↓
Source Mapping
 ↓
Knowledge Mapping
 ↓
Build
 ↓
Validate
 ↓
Activate
```

### Failure Tests

Test:

```text
Missing Knowledge
Missing Index
Invalid Configuration
Failed Build
Failed Validation
Missing Model
Concurrent Activation
```

---

## 6.71 Phase 6 Completion Criteria

Phase 6 is complete when:

- [ ] Expert entity defined
- [ ] Expert identity defined
- [ ] Domain model defined
- [ ] Knowledge scope defined
- [ ] Source mapping defined
- [ ] Expert configuration defined
- [ ] Retrieval configuration contract defined
- [ ] Generation configuration contract defined
- [ ] Evidence configuration defined
- [ ] Version policy defined
- [ ] Expert lifecycle state machine defined
- [ ] Expert versioning defined
- [ ] Expert snapshots defined
- [ ] Dependency model defined
- [ ] Readiness checks defined
- [ ] Health model defined
- [ ] Expert registry defined
- [ ] Lifecycle events defined
- [ ] Auditability defined
- [ ] Activation/deactivation defined
- [ ] Update mechanism defined
- [ ] Failure handling defined
- [ ] Idempotency defined
- [ ] Concurrency control defined
- [ ] Phase 4 contract defined
- [ ] Phase 5 contract defined
- [ ] Retrieval runtime contract defined
- [ ] Evaluation contract defined
- [ ] MVP scope defined
- [ ] Testing strategy defined

---

## 6.72 Final Architecture

```text
                         SIP
                          │
                    EXPERT REGISTRY
                          │
        ┌─────────────────┼─────────────────┐
        ↓                 ↓                 ↓
   PYTHON EXPERT     DOCKER EXPERT    POSTGRES EXPERT
        │                 │                 │
        ↓                 ↓                 ↓
   EXPERT VERSION    EXPERT VERSION    EXPERT VERSION
        │                 │                 │
        ↓                 ↓                 ↓
 KNOWLEDGE SCOPE    KNOWLEDGE SCOPE    KNOWLEDGE SCOPE
        │                 │                 │
        ↓                 ↓                 ↓
 SOURCE MAPPING     SOURCE MAPPING     SOURCE MAPPING
        │                 │                 │
        └─────────────────┼─────────────────┘
                          ↓
                   EXPERT LIFECYCLE
                          │
             ┌────────────┼────────────┐
             ↓            ↓            ↓
           BUILD       VALIDATE      HEALTH
             │            │            │
             └────────────┼────────────┘
                          ↓
                       ACTIVE
                          │
                          ↓
                  RUNTIME SNAPSHOT
                          │
                          ↓
                  RETRIEVAL SYSTEM
```
