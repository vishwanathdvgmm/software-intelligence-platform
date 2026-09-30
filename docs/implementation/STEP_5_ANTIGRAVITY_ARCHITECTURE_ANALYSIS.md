# STEP 5 — ANTIGRAVITY ARCHITECTURE ANALYSIS

## Objective

Before writing implementation code, Antigravity must first understand the complete Software Intelligence Platform (SIP) architecture and prepare an implementation plan.

**Do not begin large-scale code generation at this stage.**

The purpose of this step is to ensure that the implementation is based on the complete architecture rather than isolated interpretation of individual phase documents.

---

# 1. READ ALL PROJECT DOCUMENTATION

Read the following documents completely:

```text
Phase 1.md
Phase 2.md
Phase 3.md
Phase 4.md
Phase 5.md
Phase 6.md
Phase 7.md
Phase 8.md
Phase 9.md
Phase 10.md

SIP_IMPLEMENTATION_MASTER.md
ANTIGRAVITY_IMPLEMENTATION_INSTRUCTIONS.md
ANTIGRAVITY_MASTER_PROMPT.md
```

Do not inspect only headings or summaries.

Understand the actual:

- objectives
- components
- interfaces
- workflows
- data flow
- dependencies
- constraints
- implementation requirements
- testing requirements
- architectural decisions

---

# 2. AUDIT THE EXISTING REPOSITORY

After understanding the documentation, inspect the complete repository.

Identify:

```text
Current Project Structure
Source Code
Configuration
Dependencies
Database Layer
Vector Database Layer
RAG Components
API Layer
LLM Components
UI/Desktop Components
Tests
Scripts
Documentation
Deployment Files
```

Classify existing implementation as:

```text
IMPLEMENTED
PARTIALLY IMPLEMENTED
PLACEHOLDER
MISSING
BROKEN
UNCLEAR
```

Do not rewrite existing code simply because it is unfamiliar.

Determine whether existing components can be reused, extended, or refactored.

---

# 3. BUILD THE ARCHITECTURE MAP

Create a clear understanding of the complete SIP architecture.

At minimum map:

```text
Product Layer
        ↓
System Architecture
        ↓
Adaptive RAG Engine
        ↓
Data Layer
        ↓
Knowledge Ingestion
        ↓
Expert System
        ↓
LLM Gateway / Tools / Agent Runtime
        ↓
Desktop Application
        ↓
Evaluation / Benchmarking / Observability
        ↓
Security / Deployment / Enterprise
```

Also identify the dependencies between these systems.

Do not assume that the numerical phase order alone represents every implementation dependency.

---

# 4. TRACE THE END-TO-END DATA FLOW

Understand how information moves through the system.

At minimum trace:

```text
Knowledge Source
      ↓
Ingestion
      ↓
Processing
      ↓
Chunking
      ↓
Metadata
      ↓
Embeddings / Indexing
      ↓
Knowledge Storage
      ↓
Expert
      ↓
User Query
      ↓
Query Analysis
      ↓
Retrieval Strategy
      ↓
Semantic Retrieval
      +
Lexical Retrieval using BM25S
      ↓
Result Fusion
      ↓
Cross-Encoder Reranking
      ↓
Context Optimization
      ↓
Evidence Gating
      ↓
LLM Gateway
      ↓
Grounded Generation
      ↓
Citation / Answer
      ↓
Evaluation / Observability
```

Understand which components produce, consume, transform, or persist each piece of information.

---

# 5. IDENTIFY CORE INTERFACES

Identify the interfaces/contracts that must exist between major components.

Examples include:

```text
Document
Chunk
Knowledge Record
Embedding
Retrieval Result
Reranking Result
Context
Evidence
Expert
LLM Request
LLM Response
Tool
Agent Execution
Citation
Evaluation Result
```

Determine which contracts should be shared across multiple subsystems.

Do not allow independent components to create incompatible representations of the same concept.

---

# 6. IDENTIFY IMPLEMENTATION DEPENDENCIES

Create a dependency map such as:

```text
Foundation
    ↓
Core Data Contracts
    ↓
Storage
    ↓
Knowledge Ingestion
    ↓
Retrieval
    ↓
Adaptive RAG
    ↓
Expert Runtime
    ↓
LLM Gateway
    ↓
Tools / Agents
    ↓
API / Desktop
    ↓
Evaluation
    ↓
Security / Deployment
```

Where the Phase documents specify a different dependency relationship, follow the documented architecture and explicitly report the difference.

---

# 7. IDENTIFY ARCHITECTURAL RISKS

Before implementation, identify potential issues such as:

```text
Circular Dependencies
Missing Interfaces
Inconsistent Data Contracts
Unclear Ownership
Storage Coupling
Provider Coupling
RAG Pipeline Coupling
Security Boundaries
Performance Bottlenecks
Testing Gaps
Deployment Constraints
```

Do not silently redesign the architecture to solve these issues.

Report them for review when they represent architectural changes.

---

# 8. CREATE THE IMPLEMENTATION PLAN

After repository and architecture analysis, produce a concrete implementation plan.

The plan must identify:

```text
Implementation Area
Required Components
Dependencies
Existing Components to Reuse
New Components Required
Tests Required
Integration Points
Potential Risks
```

Organize the plan around the implementation milestones defined in:

```text
SIP_IMPLEMENTATION_MASTER.md
```

Do not create a new roadmap that conflicts with the master implementation roadmap.

---

# 9. DEFINE THE FIRST IMPLEMENTATION TARGET

Determine what must be implemented first based on:

```text
Architecture Dependencies
Repository State
Required Interfaces
Existing Implementation
Master Roadmap
```

The first implementation target must establish the foundation required for subsequent SIP components.

Do not begin by building the entire application UI or agent system.

---

# 10. ARCHITECTURE CHANGE CHECK

Before implementation begins, identify whether any existing architecture decision appears technically problematic.

For every such issue, report:

```text
Architecture Decision:
...

Observed Problem:
...

Affected Phase:
...

Affected Components:
...

Technical Impact:
...

Proposed Alternative:
...

Implementation Consequence:
...
```

Do not silently replace the documented architecture.

---

# 11. REQUIRED OUTPUT

After completing the analysis, produce:

# SIP IMPLEMENTATION READINESS REPORT

Use exactly this structure:

```text
## 1. Repository Summary

## 2. Architecture Summary

## 3. Phase Dependency Understanding

## 4. Existing Implementation Status

## 5. Missing Components

## 6. Core Interface / Contract Map

## 7. End-to-End Data Flow

## 8. Architectural Risks

## 9. Implementation Plan

## 10. First Implementation Target

## 11. Architecture Changes Requiring Review

## 12. Questions / Blockers
```

The report must be based on the actual repository and the provided SIP documentation.

Do not fabricate implementation status.

---

# 12. STOP CONDITION

After producing the:

```text
SIP IMPLEMENTATION READINESS REPORT
```

do not immediately generate thousands of lines of implementation code.

The purpose of Step 5 is:

```text
Understand
    ↓
Inspect
    ↓
Map
    ↓
Analyze
    ↓
Plan
```

Only after this architecture analysis is complete should the implementation process proceed according to the milestone plan in:

```text
SIP_IMPLEMENTATION_MASTER.md
```

---

# STEP 5 COMPLETE

Expected result:

```text
SIP Architecture
       ↓
Fully Understood

Repository
       ↓
Fully Audited

Dependencies
       ↓
Mapped

Risks
       ↓
Identified

Implementation
       ↓
Planned
```

**No large-scale implementation should begin before this analysis is complete.**