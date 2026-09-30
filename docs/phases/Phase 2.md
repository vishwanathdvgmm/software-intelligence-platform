### Overall SIP Tracker

```
╔════════════════════════════════════════════════════════════╗
║             SOFTWARE INTELLIGENCE PLATFORM                 ║
║                  IMPLEMENTATION ROADMAP                    ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║  PHASE 1  → Product Definition - Completed                 ║
║  PHASE 2  → System Architecture - In Progress              ║
║  PHASE 3  → Adaptive RAG Engine                            ║
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

# Phase 2 — System Architecture

> **Project**: Software Intelligence Platform
>
> **Internal Identifier**: `software-intelligence-platform`
>
> **Phase**: 2
>
> **Status**: Architecture Specification
>
> **Architecture Style**: Modular Monolith + Explicit Subsystem Boundaries
>
> **Primary Backend**: Python / FastAPI
>
> **Desktop Client**: Tauri + React + TypeScript

## 2.1 Architecture Objective

The Software Intelligence Platform (SIP) requires an architecture capable of supporting:

- specialized Software Experts
- continuously evolving software knowledge
- adaptive retrieval
- version-aware intelligence
- evidence-driven generation
- multiple LLM providers
- future tool integration
- desktop application workflows
- asynchronous knowledge processing
- measurable evaluation
- secure and controlled software interaction

The architecture must therefore separate **product concerns**, **knowledge concerns**, **retrieval concerns**, **generation concerns**, and **execution concerns**.

The architecture must also allow individual subsystems to evolve without requiring the entire platform to be redesigned.

### Architectural Objective

> **Build a modular, observable, secure, provider-agnostic and evidence-driven software intelligence system whose retrieval engine, knowledge system, expert system, and software interaction capabilities can evolve independently while remaining integrated through explicit contracts.**

---

## 2.2 Architecture Principles

### 2.2.1 Modular Monolith First

SIP will initially be implemented as a **modular monolith** rather than a distributed microservice system.

The application will have strong internal module boundaries while running as a unified backend deployment.

#### **Reason**

This provides:

- simpler development
- lower operational complexity
- easier debugging
- simpler local deployment
- easier transactional consistency
- clear architectural boundaries
- future extraction into services if required

Microservices are not an architectural goal.

They are an extraction strategy that may be used when scale or operational requirements justify them.

---

### 2.2.2 API-First Architecture

The desktop application must communicate with the backend through defined APIs.

The UI must not directly communicate with:

- LLM providers
- vector databases
- PostgreSQL
- retrieval engines
- knowledge processors
- external software APIs

The backend remains responsible for orchestration, authorization, validation and policy enforcement.

---

### 2.2.3 RAG Engine Independence

The Adaptive RAG Engine must remain an independent subsystem.

It must not become tightly coupled to:

- FastAPI request handling
- desktop UI
- a particular LLM provider
- a particular Software Expert
- a particular database implementation

This allows retrieval research and optimization to continue independently from the product layer.

Detailed retrieval architecture is defined in **Phase 3 — Adaptive RAG Engine**.

---

### 2.2.4 Knowledge Is a First-Class System

Knowledge is not merely a collection of vectors.

The architecture must distinguish between:

**Source**

→ where information originated

**Document**

→ canonical representation of the source material

**Document Version**

→ a particular version/snapshot

**Chunk**

→ retrievable unit derived from a document

**Embedding / Index**

→ retrieval representation

Therefore:

> **The vector database is an index, not the authoritative knowledge store.**

This principle prevents retrieval infrastructure from becoming the system of record.

Detailed data modeling belongs to Phase 4.

---

### 2.2.5 Version Awareness

Software changes over time.

Therefore the architecture must support:

- software identity
- software versions
- version-specific documentation
- version applicability
- source timestamps
- knowledge freshness
- version-aware retrieval
- version compatibility checks

A response concerning Docker 27, for example, must not silently rely on documentation describing a materially different software version.

---

### 2.2.6 Retrieval Is a Subsystem, Not a Database Query

The architecture must not equate RAG with:

> Query → Vector Search → LLM

Retrieval is a dedicated intelligence subsystem.

Its responsibilities include:

- query understanding
- retrieval planning
- candidate retrieval
- evidence selection
- ranking
- context optimization
- evidence sufficiency
- retry/reformulation
- abstention

The internal implementation is defined in Phase 3.

---

### 2.2.7 Evidence Before Generation

The generation subsystem must receive evidence produced by the retrieval system.

The architecture must support the following logical flow:

```text
User Query
    ↓
Query Understanding
    ↓
Retrieval Planning
    ↓
Evidence Retrieval
    ↓
Evidence Evaluation
    ↓
Context Construction
    ↓
LLM Generation
    ↓
Answer Validation
```

Generation must not be treated as the mechanism for discovering whether sufficient evidence exists.

---

### 2.2.8 Fail Closed

When evidence is insufficient, contradictory, stale, or version-incompatible, the system must be able to:

- retrieve again
- reformulate the query
- request clarification
- explicitly communicate uncertainty
- abstain from answering

The system must not manufacture confidence merely because an LLM can produce an answer.

---

### 2.2.9 Asynchronous Heavy Processing

Long-running workloads must not block the online conversational path.

Examples include:

- crawling
- document parsing
- normalization
- deduplication
- embedding generation
- index updates
- evaluation
- knowledge refresh

These workloads belong to asynchronous workers.

---

### 2.2.10 Provider-Agnostic LLM Architecture

The system must not depend directly on one LLM vendor.

A dedicated **LLM Gateway** will abstract:

- provider selection
- model selection
- request formatting
- streaming
- token accounting
- retries
- provider errors
- model configuration

The rest of SIP should communicate with an internal model interface rather than vendor-specific APIs.

---

### 2.2.11 Security by Default

Security is enforced at architectural boundaries rather than being added at the UI layer.

Sensitive capabilities must pass through:

```text
Request
 ↓
Authentication
 ↓
Authorization
 ↓
Policy Evaluation
 ↓
Tool Validation
 ↓
Execution
```

The desktop client cannot bypass these controls.

---

### 2.2.12 Observable by Default

Every important system operation should produce structured observability data.

The architecture must support tracing of:

- request
- expert
- retrieval run
- retrieved evidence
- model invocation
- tool invocation
- latency
- errors
- token usage
- evaluation
- citations

This is necessary for both production debugging and research evaluation.

---

## 2.3 Architecture Decisions

The following decisions form the baseline architecture.

| Area                     | Decision                                            |
| ------------------------ | --------------------------------------------------- |
| Application architecture | Modular Monolith                                    |
| Backend                  | Python                                              |
| API                      | FastAPI / REST                                      |
| Desktop                  | Tauri                                               |
| Frontend                 | React + TypeScript                                  |
| Styling                  | Tailwind CSS                                        |
| Retrieval                | Independent Adaptive RAG Engine                     |
| Retrieval model          | Hybrid + Adaptive                                   |
| Semantic index           | Qdrant initially                                    |
| System database          | PostgreSQL                                          |
| Queue / cache            | Redis                                               |
| Workers                  | Asynchronous worker system                          |
| LLM                      | Provider-agnostic                                   |
| Knowledge                | Version-aware and traceable                         |
| Raw artifacts            | Object/file storage                                 |
| Deployment               | Docker initially                                    |
| Observability            | OpenTelemetry-oriented                              |
| Security                 | Authentication + authorization + policy enforcement |
| Evaluation               | First-class subsystem                               |
| Microservices            | Deferred until justified                            |

These decisions retain the core technical direction of the original architecture while moving subsystem implementation details into later phases.

---

## 2.4 System Context

At the highest level, SIP interacts with five categories of external actors/systems.

```text
                         ┌─────────────────────┐
                         │       User          │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ SIP Desktop Client  │
                         └──────────┬──────────┘
                                    │
                                    ▼
                  ┌────────────────────────────────┐
                  │ Software Intelligence Platform │
                  └───────┬────────┬────────┬──────┘
                          │        │        │
              ┌───────────┘        │        └────────────┐
              ▼                    ▼                     ▼
       Knowledge Sources      LLM Providers       Software / Tools
       Docs / GitHub /        External Models     Docker / Git /
       Community / etc.                            VS Code / etc.
```

The user interacts primarily with the desktop application.

The platform mediates all interactions with external systems.

---

## 2.5 Container Architecture

The platform is divided into the following logical containers.

```text
┌──────────────────────────────────────────────────────────────┐
│                    SIP Desktop Application                   │
│                  Tauri + React + TypeScript                  │
└────────────────────────────┬─────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                        SIP Backend                          │
│                         FastAPI                             │
│                                                             │
│  ┌────────────┐ ┌────────────┐ ┌──────────────────────────┐ │
│  │ Auth       │ │ Chat/API   │ │ Expert System            │ │
│  └────────────┘ └────────────┘ └──────────────────────────┘ │
│                                                             │
│  ┌──────────────────┐ ┌───────────────────────────────────┐ │
│  │ Adaptive RAG     │ │ LLM Gateway                       │ │
│  └──────────────────┘ └───────────────────────────────────┘ │
│                                                             │
│  ┌──────────────────┐ ┌───────────────────────────────────┐ │
│  │ Knowledge Engine │ │ Tool / Policy Boundary            │ │
│  └──────────────────┘ └───────────────────────────────────┘ │
└─────────────┬────────────────┬────────────────┬─────────────┘
              │                │                │
              ▼                ▼                ▼
       PostgreSQL           Qdrant           Redis
              │
              ▼
        Object Storage

              +

        Async Workers
```

These are **logical containers**, not necessarily separate deployable services.

---

## 2.6 Core Component Boundaries

### 2.6.1 Desktop Application

Responsible for:

- user interaction
- workspace management
- conversations
- settings
- streaming UI
- citation presentation
- permission dialogs
- application state

Not responsible for:

- retrieval
- model calls
- authorization decisions
- database access
- tool execution

---

### 2.6.2 Platform API

The Platform API is the primary backend entry point.

Responsibilities:

- request validation
- authentication
- authorization
- API routing
- request lifecycle management
- streaming responses
- coordination with platform modules

It should remain relatively thin.

Business intelligence should reside in domain modules rather than API endpoints.

---

### 2.6.3 Expert System

Responsible for resolving:

```text
User
   ↓
Selected Software
   ↓
Software Expert
   ↓
Expert Configuration
   ↓
Knowledge Scope + Retrieval Policy + Tools
```

The Expert System determines **which expert configuration should handle a request**.

It does not itself implement the retrieval algorithms.

---

### 2.6.4 Adaptive RAG Engine

Responsible for transforming:

```text
User Query
        ↓
Evidence
        ↓
Optimized Context
```

It owns retrieval intelligence.

It does not own:

- conversation UI
- source crawling
- database schema
- LLM provider implementation

---

### 2.6.5 Knowledge Engine

Responsible for the lifecycle of software knowledge.

Conceptually:

```text
External Source
      ↓
Knowledge Processing
      ↓
Canonical Knowledge
      ↓
Retrieval Index
```

The Knowledge Engine provides knowledge to the retrieval system.

Detailed ingestion architecture belongs to Phase 5.

---

### 2.6.6 LLM Gateway

The LLM Gateway provides a unified interface to model providers.

Conceptually:

```text
Generation Request
       ↓
LLM Gateway
       ↓
Provider Adapter
       ↓
External LLM
       ↓
Normalized Response
```

This prevents model-provider details from leaking throughout the platform.

---

### 2.6.7 Tool / Policy Boundary

Future software interaction must pass through a controlled boundary.

Example:

```text
Expert
  ↓
Tool Request
  ↓
Policy Engine
  ↓
Permission Check
  ↓
Tool Adapter
  ↓
Software
```

No arbitrary command execution is permitted through the architecture.

---

## 2.7 System Data Flow

SIP has two fundamentally different workloads.

### Online Path

Handles user conversations.

```text
User
 ↓
Desktop
 ↓
API
 ↓
Authentication
 ↓
Expert Resolution
 ↓
Conversation Context
 ↓
Adaptive RAG
 ↓
Evidence
 ↓
LLM Gateway
 ↓
Answer Validation
 ↓
Response
 ↓
Desktop
```

---

### Offline Path

Handles knowledge construction and maintenance.

```text
External Sources
 ↓
Source Discovery
 ↓
Acquisition
 ↓
Knowledge Processing
 ↓
Canonical Knowledge
 ↓
Index Construction
 ↓
Knowledge Available to Experts
```

The two paths must remain logically independent.

A crawling failure should not inherently break an already operational chat session.

---

## 2.8 Online Request Architecture

The complete online request path is:

```text
┌──────────────┐
│    User      │
└──────┬───────┘
       ↓
┌──────────────┐
│   Desktop    │
└──────┬───────┘
       ↓
┌──────────────┐
│     API      │
└──────┬───────┘
       ↓
┌──────────────┐
│ Auth / Policy│
└──────┬───────┘
       ↓
┌──────────────┐
│ Expert       │
│ Resolution   │
└──────┬───────┘
       ↓
┌──────────────┐
│ Conversation │
│ Context      │
└──────┬───────┘
       ↓
┌──────────────┐
│ Adaptive RAG │
└──────┬───────┘
       ↓
┌──────────────┐
│ Evidence     │
└──────┬───────┘
       ↓
┌──────────────┐
│ LLM Gateway  │
└──────┬───────┘
       ↓
┌──────────────┐
│ Validation   │
└──────┬───────┘
       ↓
┌──────────────┐
│ Answer +     │
│ Citations    │
└──────────────┘
```

### Important architectural rule

A new conversation does **not** create or train a new model.

Instead:

```text
Docker Expert
     │
     ├── Knowledge
     ├── Retrieval Policy
     ├── Version Awareness
     ├── Behavior Configuration
     └── Tool Permissions
            │
       ┌────┴────┐
       ↓         ↓
    Chat A     Chat B
```

Chat A and Chat B have independent conversation context while sharing the same Expert definition and knowledge ecosystem.

---

## 2.9 Offline Knowledge Architecture

Knowledge processing is deliberately separated from conversational execution.

```text
             ┌─────────────────┐
             │ External Sources│
             └────────┬────────┘
                      ↓
             ┌─────────────────┐
             │ Source Adapters │
             └────────┬────────┘
                      ↓
             ┌─────────────────┐
             │ Knowledge Engine│
             └────────┬────────┘
                      ↓
             ┌─────────────────┐
             │ Canonical Store │
             └────────┬────────┘
                      ↓
             ┌─────────────────┐
             │ Retrieval Index │
             └─────────────────┘
```

Heavy operations execute asynchronously.

```text
API
 ↓
Job Creation
 ↓
Redis / Queue
 ↓
Worker
 ↓
Knowledge Processing
 ↓
Persistence
 ↓
Index Update
```

Detailed source adapters, crawling, parsing, chunking, deduplication and embedding pipelines are deferred to **Phase 5**.

---

## 2.10 External System Boundaries

SIP will potentially communicate with:

### Knowledge Sources

- official documentation
- release information
- GitHub
- community discussions
- issue trackers
- blogs
- other software-specific sources

### LLM Providers

External model providers are accessed only through the LLM Gateway.

### Software Tools

Future integrations may include:

- Docker
- Git
- VS Code
- terminals
- local development environments

These integrations must pass through explicit tool adapters and security policies.

---

## 2.11 Deployment Architecture

Initial deployment should remain operationally simple.

```text
┌───────────────────────────────┐
│       Desktop Machine         │
│                               │
│  ┌─────────────────────────┐  │
│  │ SIP Desktop             │  │
│  │ Tauri + React           │  │
│  └────────────┬────────────┘  │
│               │               │
│  ┌────────────▼────────────┐  │
│  │ SIP Backend / Runtime   │  │
│  │ Python + FastAPI        │  │
│  └────────────┬────────────┘  │
│               │               │
│        Local / Remote         │
│        infrastructure         │
└───────────────────────────────┘
```

The architecture must support a hybrid evolution:

```text
                 ┌───────────────┐
                 │ Desktop Client│
                 └───────┬───────┘
                         │
                    API / Auth
                         │
                         ▼
                 ┌───────────────┐
                 │ Cloud Backend │
                 └───────┬───────┘
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
      PostgreSQL       Qdrant         Workers
```

The exact cloud infrastructure is intentionally not locked during Phase 2.

---

## 2.12 Security Boundaries

Security is organized into layers.

```text
┌──────────────────────┐
│ Desktop Application  │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ Authentication       │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ Authorization        │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ Expert Permissions   │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ Tool Policy          │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ Tool Adapter         │
└──────────┬───────────┘
           ↓
      External System
```

### Tool Risk Model

Future tools should be classified conceptually as:

| Risk        | Example                   |
| ----------- | ------------------------- |
| READ        | inspect container status  |
| WRITE       | create/edit configuration |
| DESTRUCTIVE | remove container/data     |

The MVP should prioritize read-only functionality.

---

## 2.13 Scalability Strategy

The initial architecture optimizes for **modularity and correctness**, not premature distributed scaling.

Scaling should occur along explicit boundaries.

### Application Scaling

FastAPI instances can eventually scale horizontally.

### Worker Scaling

Knowledge processing workers can scale independently from API instances.

### Retrieval Scaling

Retrieval infrastructure can scale independently when workload requires it.

### Storage Scaling

PostgreSQL, Qdrant, object storage and Redis can evolve independently.

### Service Extraction

A module should become a separate service only when justified by factors such as:

- independent scaling requirement
- independent deployment requirement
- resource isolation
- operational isolation
- reliability boundary
- team ownership

---

## 2.14 Observability Architecture

Observability must cross subsystem boundaries.

A conceptual request trace:

```text
Request
 │
 ├── Expert Resolution
 │
 ├── Retrieval Run
 │    ├── Query Analysis
 │    ├── Retrieval Strategy
 │    ├── Candidate Retrieval
 │    ├── Reranking
 │    └── Evidence Evaluation
 │
 ├── LLM Generation
 │
 ├── Answer Validation
 │
 └── Response
```

Important telemetry should include:

- request ID
- conversation ID
- expert ID
- retrieval run ID
- model/provider
- retrieval strategy
- latency
- token usage
- evidence identifiers
- errors
- retry count
- final outcome

This enables both production observability and research evaluation.

---

## 2.15 Conversation Isolation

SIP must distinguish:

### Shared Expert State

Shared across conversations:

- software identity
- expert configuration
- knowledge scope
- retrieval policies
- version information
- tool permissions

### Conversation State

Isolated per conversation:

- messages
- temporary context
- current reasoning state
- conversation-specific references

Architecture:

```text
                 ┌───────────────┐
                 │ Docker Expert │
                 └───────┬───────┘
                         │
              ┌──────────┴──────────┐
              ↓                     ↓
        Conversation A        Conversation B
        ───────────────       ───────────────
        Messages A            Messages B
        Context A             Context B
```

Conversation A must not implicitly leak temporary conversational state into Conversation B.

---

## 2.16 Failure Boundaries

The architecture must define failure isolation.

Examples:

### LLM Provider Failure

Should not corrupt:

- knowledge
- retrieval index
- conversation history

### Knowledge Job Failure

Should not automatically terminate:

- existing conversations
- previously valid knowledge

### Qdrant Failure

Should be detectable independently from PostgreSQL.

### External Source Failure

Should not erase the last known valid knowledge state.

### Tool Failure

Should not be interpreted as successful tool execution.

This principle supports the broader **fail-closed** architecture.

---

## 2.17 Architecture Constraints

The following constraints are locked for the current architecture.

1. SIP is a **desktop-first application**, not merely a web application.
2. Backend logic is Python-based.
3. FastAPI provides the primary API boundary.
4. The desktop client uses Tauri + React + TypeScript.
5. Adaptive RAG is an independent subsystem.
6. LLM providers are abstracted through a gateway.
7. PostgreSQL is the authoritative structured data store.
8. Qdrant is a retrieval index rather than the knowledge source of truth.
9. Redis supports asynchronous processing and caching responsibilities.
10. Heavy knowledge processing is asynchronous.
11. Knowledge is version-aware.
12. Evidence and citations are first-class concepts.
13. Tool execution is permission-controlled.
14. The initial architecture is a modular monolith.
15. Microservices are deferred.
16. Evaluation and observability are architectural concerns rather than post-development additions.

---

## 2.18 Architecture Boundaries — What Does NOT Belong in Phase 2

To prevent architecture drift, the following are intentionally deferred.

| Topic                                      |     Phase |
| ------------------------------------------ | --------: |
| Query classification                       |   Phase 3 |
| Retrieval strategy algorithms              |   Phase 3 |
| BM25S implementation                       |   Phase 3 |
| RRF implementation                         |   Phase 3 |
| Cross-encoder configuration                |   Phase 3 |
| Context optimization                       |   Phase 3 |
| Evidence scoring                           |   Phase 3 |
| Retry/reformulation                        |   Phase 3 |
| Database schema                            |   Phase 4 |
| Chunk schema                               |   Phase 4 |
| Embedding schema                           |   Phase 4 |
| Source adapters                            |   Phase 5 |
| Crawling implementation                    |   Phase 5 |
| Parsing/normalization                      |   Phase 5 |
| Deduplication implementation               |   Phase 5 |
| Expert manifest internals                  |   Phase 6 |
| Expert lifecycle implementation            |   Phase 6 |
| Tool registry implementation               | Phase 6/7 |
| Agent runtime                              |   Phase 7 |
| Desktop UI implementation                  |   Phase 8 |
| Evaluation datasets/metrics implementation |   Phase 9 |
| Production hardening                       |  Phase 10 |

This is the major structural correction from the previous Phase 2.

---

## 2.19 Phase 2 → Phase 3 Contract

Phase 2 defines the **boundary** for the Adaptive RAG Engine.

Phase 3 must implement the internal retrieval intelligence behind this interface:

```text
Input
─────
Query
Expert Context
Software Identity
Version Context
Retrieval Policy
Conversation Context


Output
──────
Retrieved Evidence
Optimized Context
Citations
Evidence Status
Retrieval Metadata
```

Conceptually:

```text
                    ┌───────────────────┐
                    │   Expert System   │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │   Adaptive RAG    │
                    │                   │
                    │  Analyze          │
                    │  Plan             │
                    │  Retrieve         │
                    │  Fuse             │
                    │  Rerank           │
                    │  Optimize         │
                    │  Evaluate         │
                    │  Retry / Abstain  │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ Evidence + Context│
                    └───────────────────┘
```

Phase 3 owns **how retrieval intelligence works**.

Phase 2 owns **where that subsystem lives and how the rest of SIP interacts with it**.

---

## 2.20 Phase 2 Completion Criteria

Phase 2 is considered architecturally complete when the following are defined:

- [x] architecture principles
- [x] major architecture decisions
- [x] system context
- [x] container architecture
- [x] subsystem boundaries
- [x] online request flow
- [x] offline knowledge flow
- [x] external system boundaries
- [x] deployment direction
- [x] security boundaries
- [x] scalability strategy
- [x] observability boundary
- [x] conversation isolation
- [x] failure boundaries
- [x] architecture constraints
- [x] Phase 2 → Phase 3 contract
- [x] separation from later phases

---

# Final Architecture

The resulting SIP architecture can be summarized as:

```text
                         USER
                          │
                          ▼
                ┌────────────────────┐
                │   SIP Desktop      │
                │ Tauri + React + TS │
                └─────────┬──────────┘
                          │
                          ▼
                ┌───────────────────┐
                │    FastAPI API    │
                └─────────┬─────────┘
                          │
          ┌───────────────┼────────────────┐
          │               │                │
          ▼               ▼                ▼
    ┌───────────┐   ┌─────────────┐  ┌────────────┐
    │   Auth    │   │    Expert   │  │   Policy   │
    └───────────┘   │    System   │  └────────────┘
                    └──────┬──────┘
                           │
                           ▼
                 ┌──────────────────┐
                 │  Adaptive RAG    │
                 │    Engine        │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ Evidence /       │
                 │ Context          │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │   LLM Gateway    │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ Answer Validator │
                 └────────┬─────────┘
                          │
                          ▼
                        USER


        ───────────── OFFLINE KNOWLEDGE PLANE ─────────────

 External Sources
       │
       ▼
 Knowledge Engine
       │
       ▼
 PostgreSQL ───────────────► Qdrant
       │
       ▼
 Object Storage

       ▲
       │
 Async Workers / Redis
```
