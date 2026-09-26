### Overall SIP Tracker

```
╔══════════════════════════════════════════════════════════════╗
║             SOFTWARE INTELLIGENCE PLATFORM                   ║
║                  IMPLEMENTATION ROADMAP                      ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  PHASE 1  → Product Definition - Completed                   ║
║  PHASE 2  → System Architecture - Completed                  ║
║  PHASE 3  → Adaptive RAG Engine - Completed                  ║
║  PHASE 4  → Data Layer & Knowledge Storage - Completed       ║
║  PHASE 5  → Knowledge Ingestion & Crawling - Completed       ║
║  PHASE 6  → Expert System & Expert Lifecycle - Completed     ║
║  PHASE 7  → LLM Gateway, Tools & Agent Runtime - In Progress ║
║  PHASE 8  → Desktop Application Architecture                 ║
║  PHASE 9  → Evaluation, Benchmarking & Observability         ║
║  PHASE 10 → Security, Deployment & Enterprise                ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

> **Project:** Software Intelligence Platform
>
> **Phase:** 7
>
> **Subsystem:** LLM Gateway, Tool System & Agent Runtime
>
> **Status:** Implementation Specification

---

## 7.1 Phase Objective

Phase 7 SIP ke intelligent execution layer ko define karta hai.

Phase 6 mein humne **Expert** define kiya tha.

Ab Phase 7 ka responsibility hai:

```text
Expert
   ↓
Agent Runtime
   ↓
LLM Gateway
   ↓
Tool System
   ↓
Controlled Execution
```

The system should provide a controlled runtime in which an Expert can:

- communicate with an LLM
- select appropriate tools
- execute tools
- observe tool results
- continue reasoning
- interact with retrieval systems
- maintain execution state
- enforce limits
- produce a final structured result

---

## 7.2 Core Architectural Principle

Traditional LLM application:

```text
User
 ↓
Prompt
 ↓
LLM
 ↓
Answer
```

SIP:

```text
User
 ↓
Expert
 ↓
Agent Runtime
 ↓
LLM Gateway
 ↓
Decision
 ↓
Tool / Retrieval / Internal Service
 ↓
Observation
 ↓
Agent Runtime
 ↓
LLM
 ↓
Validation
 ↓
Final Answer
```

The runtime controls the loop.

The LLM does **not** directly control the operating system or application internals.

---

## 7.3 Responsibilities of Phase 7

Phase 7 owns:

- LLM provider abstraction
- LLM request normalization
- model configuration
- provider routing
- retry handling
- timeout handling
- token/cost tracking
- tool registry
- tool definitions
- tool validation
- tool execution
- tool permissions
- execution context
- agent loop
- iteration limits
- execution budgets
- runtime state
- tool observations
- final response handling
- runtime errors
- execution tracing

---

## 7.4 What Phase 7 Does NOT Own

Phase 7 does **not** own:

- document crawling
- document extraction
- knowledge storage
- chunking
- embedding generation
- vector database implementation
- BM25S implementation
- Expert lifecycle
- source acquisition
- UI implementation

These belong to other subsystems.

Conceptually:

```text
Phase 4
→ Data Layer

Phase 5
→ Knowledge Ingestion

Phase 6
→ Expert System

Phase 7
→ Intelligence Execution Runtime
```

---

## 7.5 High-Level Architecture

```text
                         USER REQUEST
                              │
                              ↓
                       ┌──────────────┐
                       │    EXPERT    │
                       └──────┬───────┘
                              ↓
                    ┌────────────────────┐
                    │   AGENT RUNTIME    │
                    └─────────┬──────────┘
                              ↓
                    ┌────────────────────┐
                    │    LLM GATEWAY     │
                    └─────────┬──────────┘
                              ↓
                         LLM PROVIDER
                              │
                              ↓
                         LLM RESPONSE
                              │
                ┌─────────────┴─────────────┐
                ↓                           ↓
          FINAL ANSWER                 TOOL CALL
                                            │
                                            ↓
                                    ┌──────────────┐
                                    │ TOOL SYSTEM  │
                                    └──────┬───────┘
                                           ↓
                                       TOOL RESULT
                                           │
                                           ↓
                                    AGENT RUNTIME
                                           │
                                           ↓
                                         LLM
```

---

## 7.6 LLM Gateway

The LLM Gateway provides a unified interface to different LLM providers.

Instead of application code directly calling:

```text
OpenAI
Anthropic
Gemini
Ollama
etc.
```

the application calls:

```text
LLM Gateway
```

Example:

```python
response = llm_gateway.generate(request)
```

The gateway determines how that request reaches the configured provider.

---

## 7.7 Why an LLM Gateway?

Without a gateway:

```text
Application
 ├── OpenAI code
 ├── Gemini code
 ├── Anthropic code
 └── Ollama code
```

This creates provider coupling.

With gateway:

```text
Application
      ↓
LLM Gateway
      ↓
Provider Adapter
      ↓
LLM Provider
```

This provides:

- provider abstraction
- model switching
- centralized configuration
- centralized logging
- retries
- rate limiting
- cost tracking
- fallback support

---

## 7.8 Provider Adapter Architecture

```text
LLM Gateway
     │
     ├── OpenAI Adapter
     ├── Gemini Adapter
     ├── Anthropic Adapter
     └── Ollama Adapter
```

Each adapter implements a common interface.

Conceptually:

```python
class LLMProvider:
    def generate(...)
    def stream(...)
```

The exact interface should be finalized during implementation.

---

## 7.9 Normalized LLM Request

The gateway should receive a provider-independent request.

Conceptually:

```text
LLMRequest
│
├── model
├── messages
├── system_instruction
├── tools
├── temperature
├── max_tokens
├── response_format
├── timeout
└── metadata
```

Provider-specific parameters should remain inside the adapter where possible.

---

## 7.10 Normalized LLM Response

The gateway should normalize provider responses.

Conceptually:

```text
LLMResponse
│
├── content
├── tool_calls
├── finish_reason
├── usage
├── model
├── provider
└── metadata
```

This prevents downstream code from depending on provider-specific response formats.

---

## 7.11 Streaming

The gateway should support streaming where the provider supports it.

```text
LLM
 ↓
Token/Event Stream
 ↓
LLM Gateway
 ↓
Runtime
 ↓
Application
```

Streaming is especially useful for interactive applications.

---

## 7.12 Non-Streaming Execution

For internal reasoning or tool execution, normal request/response mode may be preferable.

```text
Request
 ↓
LLM
 ↓
Complete Response
```

The runtime should support both modes.

---

## 7.13 Model Configuration

Model selection should be configuration-driven.

Example:

```text
Expert
   ↓
Generation Config
   ↓
Model Profile
   ↓
LLM Gateway
```

Example:

```text
model_profile:
    provider = ollama
    model = qwen
```

or:

```text
model_profile:
    provider = openai
    model = configured-model
```

Exact model names should not be hard-coded into business logic.

---

## 7.14 Model Profiles

A model profile can define:

```text
ModelProfile
│
├── provider
├── model
├── context_limit
├── capabilities
├── timeout
├── temperature
└── token_limit
```

Capabilities may include:

```text
TEXT_GENERATION
TOOL_CALLING
STRUCTURED_OUTPUT
STREAMING
VISION
```

Only capabilities actually supported by the configured model should be enabled.

---

## 7.15 Provider Routing

The gateway may eventually support routing:

```text
Request
   ↓
Model Router
   ├── Primary Model
   ├── Secondary Model
   └── Fallback Model
```

For MVP:

```text
One configured provider
        ↓
One configured model
```

Keep the abstraction ready for future routing.

---

## 7.16 Retry Policy

Transient LLM failures should be handled by the gateway.

Possible retryable failures:

```text
Timeout
Temporary network failure
Rate limit
Temporary provider error
```

Non-retryable errors should fail immediately.

---

## 7.17 Retry Constraints

Retries must be bounded.

Example:

```text
max_retries = 2
```

Never:

```text
LLM failure
 ↓
retry forever
```

because this can cause:

- latency explosion
- cost explosion
- request duplication

---

## 7.18 Timeout Management

Each LLM call should have a timeout.

```text
LLM Request
      ↓
Timeout
      ↓
Abort / Retry
```

Timeout should be configurable per model profile.

---

## 7.19 Token Usage Tracking

Every LLM call should record usage where available.

Example:

```text
input_tokens
output_tokens
total_tokens
```

This allows:

- cost estimation
- debugging
- optimization
- budget enforcement

---

## 7.20 Cost Tracking

If provider pricing metadata is configured, the gateway can calculate:

```text
estimated_cost
```

Example:

```text
Request
 ↓
Token Usage
 ↓
Pricing Profile
 ↓
Estimated Cost
```

Cost tracking should be observational initially.

Hard budget enforcement can be added at runtime level.

---

## 7.21 Tool System

Tools allow the Expert runtime to perform controlled operations outside pure text generation.

Examples:

```text
Knowledge Search
Document Lookup
Code Analysis
Database Query
Filesystem Read
Calculator
Metadata Lookup
```

Not every tool should be available to every Expert.

---

## 7.22 Tool Registry

The system should maintain a central Tool Registry.

```text
Tool Registry
│
├── knowledge_search
├── document_lookup
├── metadata_lookup
├── calculator
└── code_analysis
```

The registry stores:

```text
tool_id
name
description
input_schema
output_schema
permissions
executor
version
status
```

---

## 7.23 Tool Definition

A tool should have a machine-readable definition.

Example:

```text
Tool:
    name = knowledge_search

    description =
        Search the Expert knowledge base.

    input:
        query: string
        limit: integer

    output:
        results: list
```

The schema is important because the LLM needs to know how to call the tool.

---

## 7.24 Tool Input Validation

LLM-generated tool arguments must never be trusted directly.

Flow:

```text
LLM Tool Call
     ↓
Parse Arguments
     ↓
Schema Validation
     ↓
Permission Check
     ↓
Tool Execution
```

Invalid arguments should be rejected before execution.

---

## 7.25 Tool Output Validation

Tool output should also be normalized.

```text
Tool
 ↓
Raw Result
 ↓
Output Validation
 ↓
ToolResult
```

This prevents malformed tool results from corrupting runtime state.

---

## 7.26 Tool Permissions

Each Expert should have a tool permission set.

Example:

```text
Python Expert
    ✓ knowledge_search
    ✓ document_lookup
    ✓ code_analysis
    ✗ database_write
```

The LLM cannot bypass this configuration.

---

## 7.27 Tool Permission Levels

Potential permission model:

```text
READ
EXECUTE
WRITE
ADMIN
```

For MVP, keep it simpler:

```text
ALLOWED
DENIED
```

Expand later if required.

---

## 7.28 Tool Safety Boundary

Critical rule:

> **The LLM should never directly execute arbitrary Python, shell commands, SQL, filesystem operations, or network requests.**

If such capabilities are eventually required, they must exist as explicitly registered and permission-controlled tools.

Example:

```text
LLM
 ↓
"execute_shell_command"
 ↓
Permission System
 ↓
Sandbox
 ↓
Execution
```

Not:

```text
LLM → os.system(...)
```

---

## 7.29 Tool Execution Model

```text
Tool Call
   ↓
Registry Lookup
   ↓
Tool Exists?
   ↓
Permission Check
   ↓
Input Validation
   ↓
Execution
   ↓
Output Validation
   ↓
Observation
```

---

## 7.30 Tool Result

Tool results should have a standardized structure.

```text
ToolResult
│
├── tool_id
├── success
├── data
├── error
├── metadata
└── execution_time
```

Example:

```text
success = true

data:
    [
        ...
    ]
```

---

## 7.31 Tool Failure

A tool failure should become an observation rather than crash the entire runtime where possible.

```text
Tool
 ↓
Failure
 ↓
ToolResult(success=false)
 ↓
Agent Runtime
 ↓
LLM decides whether to retry / change strategy / stop
```

The runtime itself should enforce retry limits.

---

## 7.32 Agent Runtime

The Agent Runtime is the execution engine.

Its responsibility is to manage:

```text
Request
 ↓
Context
 ↓
LLM
 ↓
Tool Call
 ↓
Observation
 ↓
LLM
 ↓
Final Result
```

---

## 7.33 Agent Runtime Is NOT the LLM

This distinction is important.

```text
LLM
→ reasoning/generation component

Agent Runtime
→ execution/control component
```

Therefore:

```text
LLM ≠ Agent
```

An agent is the combination of:

```text
LLM
+
Tools
+
State
+
Control Loop
+
Policies
```

---

## 7.34 Agent Execution Loop

Basic runtime:

```text
START
  ↓
Build Context
  ↓
Call LLM
  ↓
Response
  ↓
Tool Call?
 /       \
NO        YES
↓          ↓
Validate   Execute Tool
↓          ↓
FINAL    Observation
           ↓
         Call LLM
```

---

## 7.35 Maximum Iterations

The runtime must have a hard iteration limit.

Example:

```text
max_iterations = 8
```

Flow:

```text
Iteration 1
Iteration 2
...
Iteration 8
     ↓
STOP
```

This prevents infinite loops.

---

## 7.36 Execution Budget

The runtime should support budgets.

Possible budgets:

```text
max_iterations
max_tool_calls
max_execution_time
max_tokens
max_cost
```

Example:

```text
AgentBudget
├── max_iterations = 8
├── max_tool_calls = 6
├── timeout = configured
└── max_tokens = configured
```

---

## 7.37 Runtime Context

Every execution needs an isolated context.

```text
ExecutionContext
│
├── execution_id
├── expert_id
├── expert_version
├── user_query
├── messages
├── tool_calls
├── observations
├── budget
├── timestamps
└── metadata
```

This context should not leak between unrelated requests.

---

## 7.38 Execution ID

Every execution should have a unique ID.

Example:

```text
execution_id = exec_01...
```

This allows:

- tracing
- debugging
- audit logs
- performance analysis

---

## 7.39 Agent State

Runtime state may include:

```text
INITIALIZING
RUNNING
WAITING_FOR_TOOL
PROCESSING_OBSERVATION
COMPLETED
FAILED
CANCELLED
TIMEOUT
BUDGET_EXCEEDED
```

---

## 7.40 Runtime State Machine

```text
INITIALIZING
      ↓
RUNNING
      ↓
WAITING_FOR_TOOL
      ↓
PROCESSING_OBSERVATION
      ↓
RUNNING
      ↓
COMPLETED
```

Failure paths:

```text
RUNNING
  ├── FAILED
  ├── TIMEOUT
  ├── CANCELLED
  └── BUDGET_EXCEEDED
```

---

## 7.41 Context Assembly

Before calling the LLM, runtime constructs context.

Conceptually:

```text
Expert Instructions
        +
User Query
        +
Conversation Context
        +
Retrieved Evidence
        +
Tool Results
        ↓
     LLM Context
```

The runtime should explicitly manage what enters the context.

---

## 7.42 Context Separation

Do not mix everything into one undifferentiated prompt.

Maintain conceptual categories:

```text
SYSTEM
EXPERT_INSTRUCTIONS
USER
RETRIEVED_EVIDENCE
TOOL_RESULT
ASSISTANT
```

This makes execution easier to inspect and debug.

---

## 7.43 Tool Calls as Structured Messages

Tool calls should be represented structurally.

```text
assistant:
    tool_call:
        name = knowledge_search
        arguments = {...}
```

Then:

```text
tool:
    result = {...}
```

Do not rely only on free-form text parsing.

---

## 7.44 Tool Selection

The LLM may select a tool from the available tool definitions.

But the runtime verifies:

```text
Tool exists?
Tool enabled?
Tool allowed for Expert?
Arguments valid?
Budget available?
```

Only then execute.

---

## 7.45 Agent Tool Selection Loop

```text
LLM
 ↓
Tool Selection
 ↓
Runtime Validation
 ↓
Tool Execution
 ↓
Observation
 ↓
LLM
```

This can repeat until:

```text
Final Answer
```

or:

```text
Budget / iteration limit
```

---

## 7.46 Retrieval as a Tool

The retrieval system can be exposed to the runtime as a controlled tool.

Example:

```text
knowledge_search(
    query="Python async generators",
    limit=5
)
```

This creates a clean boundary:

```text
Agent Runtime
      ↓
Knowledge Search Tool
      ↓
Retrieval System
```

The runtime does not need to know how BM25S, vector retrieval, fusion or reranking internally work.

---

## 7.47 Expert-Aware Tools

Tools should execute within Expert context.

Example:

```text
Python Expert
     ↓
knowledge_search()
     ↓
Python Knowledge Scope
```

The tool should not automatically search unrelated Expert knowledge.

---

## 7.48 Tool Context

Tool execution should receive:

```text
execution_id
expert_id
expert_version
tool_arguments
permissions
```

This enables contextual enforcement.

---

## 7.49 Tool Isolation

Tools should be isolated from one another.

Example:

```text
Knowledge Tool
```

should not have implicit access to:

```text
Database Write Tool
```

Each tool gets only the dependencies it requires.

---

## 7.50 Agent Memory

For MVP, distinguish:

```text
Execution Context
```

from:

```text
Long-Term Memory
```

Do not automatically create persistent agent memory.

MVP should primarily use:

```text
Current request
+
Conversation context
+
Retrieved knowledge
+
Tool observations
```

Persistent memory can be a later phase.

---

## 7.51 Conversation Context

Conversation context should be bounded.

If conversation becomes too large:

```text
Conversation
 ↓
Context Management
 ↓
Relevant history
 ↓
LLM
```

Possible future strategies:

- summarization
- selective history
- semantic memory

Do not over-engineer this in MVP.

---

## 7.52 Structured Output

The LLM Gateway should support structured outputs where the model supports them.

Example:

```text
{
    "answer": "...",
    "confidence": "...",
    "citations": [...]
}
```

However, structured output does not itself guarantee factual correctness.

It only guarantees format constraints.

---

## 7.53 Final Answer Validation

Before returning the final response, runtime may perform structural validation.

Check:

```text
Required fields
Citation structure
Tool execution status
Evidence availability
Budget status
```

Semantic grounding validation belongs to the retrieval/evaluation pipeline.

---

## 7.54 Agent Stop Conditions

The agent should stop when:

```text
Final answer produced
```

or:

```text
No further tool needed
```

or:

```text
Maximum iterations reached
```

or:

```text
Budget exceeded
```

or:

```text
Execution cancelled
```

---

## 7.55 Insufficient Evidence

If the Expert's knowledge retrieval cannot provide enough evidence, the runtime should not force an answer.

Possible flow:

```text
Query
 ↓
Retrieval
 ↓
Insufficient Evidence
 ↓
Retry / Alternative Retrieval
 ↓
Still insufficient
 ↓
Grounded "Insufficient Evidence" response
```

The exact evidence threshold belongs to the retrieval/evidence subsystem.

---

## 7.56 Hallucination Boundary

The Agent Runtime should not assume:

```text
LLM answer = truth
```

Instead:

```text
LLM
 ↓
Candidate Answer
 ↓
Evidence / Validation
 ↓
Final Answer
```

This distinction is fundamental to SIP.

---

## 7.57 Tool Calling vs Autonomous Agent

SIP should initially implement **bounded agents**.

Not:

```text
Unlimited autonomous agent
```

Instead:

```text
Goal
 ↓
Bounded execution
 ↓
Limited tools
 ↓
Limited iterations
 ↓
Limited budget
 ↓
Result
```

This improves reproducibility and reliability.

---

## 7.58 Runtime Policies

Runtime policies should include:

```text
AgentPolicy
│
├── max_iterations
├── max_tool_calls
├── timeout
├── token_budget
├── cost_budget
├── allowed_tools
└── failure_policy
```

---

## 7.59 Failure Policy

Example:

```text
failure_policy:
    tool_failure = retry_once
    llm_failure = gateway_retry
    timeout = terminate
    budget_exceeded = terminate
```

These should be configuration-driven.

---

## 7.60 Cancellation

Long-running executions should support cancellation.

```text
RUNNING
   ↓
CANCEL
   ↓
CANCELLED
```

Cancellation should stop future tool execution.

Already-running external operations may require tool-specific cancellation support.

---

## 7.61 Observability

Every execution should produce trace information.

Example:

```text
Execution
│
├── LLM Call #1
├── Tool Call #1
├── Tool Result #1
├── LLM Call #2
├── Tool Call #2
├── Tool Result #2
└── Final Response
```

This is extremely useful for debugging SIP.

---

## 7.62 Runtime Metrics

Track:

```text
execution_latency
llm_latency
tool_latency
llm_calls
tool_calls
tokens_used
estimated_cost
iterations
failures
```

Later this can be used to optimize the architecture.

---

## 7.63 LLM Gateway Metrics

Gateway should track:

```text
provider
model
request_count
success_count
failure_count
latency
token_usage
retry_count
```

---

## 7.64 Tool Metrics

Each tool should track:

```text
tool_name
execution_count
success_count
failure_count
average_latency
timeout_count
```

---

## 7.65 Runtime Logging

Logs should include:

```text
execution_id
expert_id
expert_version
event
timestamp
duration
status
```

Sensitive user content should not automatically be logged in full.

---

## 7.66 Secrets Management

API keys must never be stored directly inside:

```text
Expert configuration
Tool definitions
Source code
Git repository
```

Use environment/configuration secret management.

Example:

```text
LLM Gateway
      ↓
Secret Provider
      ↓
API Key
```

---

## 7.67 Provider Abstraction Structure

Suggested implementation:

```text
llm/
│
├── gateway.py
├── models.py
├── providers/
│   ├── base.py
│   ├── openai.py
│   ├── gemini.py
│   ├── anthropic.py
│   └── ollama.py
│
├── routing/
│   └── router.py
│
├── retry/
│   └── policy.py
│
└── usage/
    └── tracker.py
```

Only implement providers actually needed for MVP.

---

## 7.68 Tool System Structure

```text
tools/
│
├── registry.py
├── models.py
├── permissions.py
├── validator.py
├── executor.py
│
├── builtins/
│   ├── knowledge_search.py
│   ├── document_lookup.py
│   └── metadata_lookup.py
│
└── sandbox/
    └── ...
```

---

## 7.69 Agent Runtime Structure

```text
agent/
│
├── runtime.py
├── context.py
├── state.py
├── loop.py
├── policies.py
├── budget.py
├── cancellation.py
├── validation.py
└── tracing.py
```

---

## 7.70 Complete Request Lifecycle

Phase 7 integrates the previous phases:

```text
USER
 ↓
Expert Resolution
 ↓
Active Expert
 ↓
Expert Snapshot
 ↓
Agent Runtime
 ↓
Context Assembly
 ↓
LLM Gateway
 ↓
LLM Decision
 ↓
 ┌───────────────────────────┐
 │                           │
 ↓                           ↓
FINAL RESPONSE             TOOL CALL
                             ↓
                       Tool Validation
                             ↓
                       Permission Check
                             ↓
                       Tool Execution
                             ↓
                          Observation
                             ↓
                       Agent Runtime
                             ↓
                           LLM
                             ↓
                    FINAL / TOOL AGAIN
```

---

## 7.71 Example — Knowledge Question

User:

> "What is Python's asyncio TaskGroup?"

Flow:

```text
User Query
   ↓
Python Expert
   ↓
Agent Runtime
   ↓
LLM
   ↓
knowledge_search
   ↓
Retrieval System
   ↓
Hybrid Retrieval
   ↓
Reranking
   ↓
Evidence
   ↓
Agent Runtime
   ↓
LLM
   ↓
Grounded Answer
```

---

## 7.72 Example — Tool-Using Question

User:

> "Find the relevant documentation and summarize the differences between two APIs."

Flow:

```text
User
 ↓
Expert
 ↓
Agent Runtime
 ↓
LLM
 ↓
knowledge_search
 ↓
Evidence
 ↓
LLM
 ↓
Final Answer
```

If another tool is necessary:

```text
LLM
 ↓
Tool A
 ↓
Observation
 ↓
LLM
 ↓
Tool B
 ↓
Observation
 ↓
Final
```

---

## 7.73 Example — Tool Failure

```text
LLM
 ↓
Tool Call
 ↓
Tool Failure
 ↓
Runtime
 ↓
Retry Policy
 ↓
Retry
 ↓
Success
 ↓
LLM
 ↓
Answer
```

If retry limit is exceeded:

```text
Tool Failure
 ↓
No Retry Remaining
 ↓
Runtime
 ↓
Controlled Failure
```

---

## 7.74 Agent Runtime Security Boundary

The following rule is mandatory:

```text
LLM output
    ≠
Trusted executable instruction
```

Every action must pass through:

```text
LLM Intent
 ↓
Runtime Validation
 ↓
Permission
 ↓
Tool
 ↓
Execution
```

This protects the system from unsafe or malformed model outputs.

---

## 7.75 Prompt Injection Consideration

Retrieved documents and tool outputs must be treated as **untrusted data**.

For example, a retrieved document might contain text such as:

```text
Ignore previous instructions...
```

The runtime must not automatically treat retrieved content as system-level instructions.

Conceptually:

```text
System Instructions
       +
Expert Instructions
       +
User Request
       +
Untrusted Evidence
```

These must remain logically separated.

---

## 7.76 Tool Result Injection

The same principle applies to tool outputs.

```text
Tool Result
```

is data.

It must not automatically override:

```text
System Policy
Expert Policy
Runtime Policy
```

---

## 7.77 Instruction Hierarchy

Runtime should conceptually preserve:

```text
System Policy
      ↓
Runtime Policy
      ↓
Expert Configuration
      ↓
User Request
      ↓
Retrieved Evidence / Tool Results
```

Retrieved information must not gain higher authority merely because it was returned by a tool.

---

## 7.78 Agent Determinism

Fully deterministic LLM behavior cannot always be guaranteed.

However, SIP should maximize reproducibility by recording:

```text
model
model configuration
expert version
knowledge version
tool versions
runtime policy
execution trace
```

This enables later reproduction and debugging.

---

## 7.79 Agent Runtime and Evaluation

Every execution should eventually be evaluatable.

```text
Execution
 ↓
Trace
 ↓
Evaluation
 ↓
Metrics
```

Possible metrics:

```text
Tool Selection Accuracy
Retrieval Quality
Groundedness
Answer Accuracy
Latency
Token Usage
Cost
```

---

## 7.80 MVP Scope

Phase 7 MVP should implement:

```text
✓ LLM Gateway
✓ One provider adapter
✓ Model configuration
✓ Normalized requests/responses
✓ Retry handling
✓ Timeout handling
✓ Token tracking
✓ Tool registry
✓ Tool schema
✓ Tool validation
✓ Tool permissions
✓ Knowledge-search tool
✓ Agent runtime
✓ Bounded agent loop
✓ Execution context
✓ Maximum iterations
✓ Tool-call limits
✓ Basic budget
✓ Runtime state
✓ Failure handling
✓ Execution tracing
```

Do **not** implement everything at once.

---

## 7.81 Deferred Features

Keep these for later:

```text
→ Multi-agent collaboration
→ Autonomous Expert creation
→ Long-term agent memory
→ Complex workflow planning
→ Dynamic model routing
→ Model ensembles
→ Self-reflection loops
→ Autonomous tool discovery
→ Distributed agent execution
```

These can significantly increase complexity.

---

## 7.82 Implementation Priority

Implement in this order:

```text
1. LLM interface
        ↓
2. Provider adapter
        ↓
3. LLM Gateway
        ↓
4. Request/response normalization
        ↓
5. Retry + timeout
        ↓
6. Usage tracking
        ↓
7. Tool model
        ↓
8. Tool registry
        ↓
9. Tool validation
        ↓
10. Tool permissions
        ↓
11. Tool executor
        ↓
12. Execution context
        ↓
13. Agent state machine
        ↓
14. Agent loop
        ↓
15. Budget enforcement
        ↓
16. Knowledge-search tool
        ↓
17. Tracing
        ↓
18. Evaluation integration
```

---

## 7.83 Suggested Test Strategy

### Unit Tests

Test:

- LLM request normalization
- provider adapters
- retry policy
- timeout policy
- token accounting
- tool schema validation
- permission checks
- budget checks
- state transitions

### Integration Tests

Test:

```text
Agent
 ↓
LLM
 ↓
Knowledge Tool
 ↓
Retrieval
 ↓
Tool Result
 ↓
LLM
 ↓
Final Answer
```

### Failure Tests

Test:

```text
LLM Timeout
LLM Rate Limit
Invalid Tool
Invalid Arguments
Permission Denied
Tool Timeout
Tool Failure
Maximum Iterations
Budget Exceeded
Cancellation
```

---

## 7.84 Phase 7 Completion Criteria

Phase 7 is complete when:

- [ ] LLM Gateway defined
- [ ] Provider abstraction defined
- [ ] Provider adapter defined
- [ ] Normalized request model defined
- [ ] Normalized response model defined
- [ ] Model profile defined
- [ ] Retry policy defined
- [ ] Timeout policy defined
- [ ] Token usage tracking defined
- [ ] Cost tracking contract defined
- [ ] Tool Registry defined
- [ ] Tool model defined
- [ ] Tool input schema defined
- [ ] Tool output schema defined
- [ ] Tool permission model defined
- [ ] Tool validation defined
- [ ] Tool execution model defined
- [ ] Tool failure handling defined
- [ ] Agent Runtime defined
- [ ] Execution Context defined
- [ ] Runtime state machine defined
- [ ] Agent loop defined
- [ ] Maximum iteration policy defined
- [ ] Tool-call budget defined
- [ ] Execution budget defined
- [ ] Cancellation defined
- [ ] Knowledge Search Tool defined
- [ ] Expert-aware tool execution defined
- [ ] Prompt-injection boundary defined
- [ ] Tool-result trust boundary defined
- [ ] Execution tracing defined
- [ ] Runtime metrics defined
- [ ] Security boundary defined
- [ ] Evaluation integration defined
- [ ] MVP scope defined
- [ ] Testing strategy defined

---

## 7.85 Phase 7 Final Architecture

```text
                           SIP
                            │
                            ↓
                         EXPERT
                            │
                            ↓
                  ┌───────────────────┐
                  │   AGENT RUNTIME   │
                  └─────────┬─────────┘
                            │
              ┌─────────────┴─────────────┐
              ↓                           ↓
        ┌───────────┐              ┌────────────┐
        │LLM GATEWAY│              │TOOL SYSTEM │
        └─────┬─────┘              └──────┬─────┘
              │                           │
       ┌──────┴───────┐             ┌─────┴────────┐
       ↓      ↓       ↓             ↓      ↓       ↓
   Provider  Model  Router      Retrieval  Docs  Metadata
       │
       ↓
      LLM
       │
       ↓
   Decision
       │
       ├──────────────→ Final Answer
       │
       └──────────────→ Tool Call
                           │
                           ↓
                     Permission
                           │
                           ↓
                       Execution
                           │
                           ↓
                       Observation
                           │
                           ↓
                     Agent Runtime
```

---

## 7.86 Critical Architectural Rules

Phase 7 ke liye ye rules implementation ke time **break nahi hone chahiye**:

### Rule 1

```text
LLM ≠ Agent Runtime
```

### Rule 2

```text
LLM output ≠ trusted executable command
```

### Rule 3

```text
Every tool call → validation + permission
```

### Rule 4

```text
Every agent execution → bounded
```

### Rule 5

```text
Retrieved content ≠ system instruction
```

### Rule 6

```text
Tool output ≠ trusted instruction
```

### Rule 7

```text
Provider-specific code stays behind LLM Gateway
```

### Rule 8

```text
Expert configuration controls available capabilities
```

### Rule 9

```text
Every execution must be traceable
```

### Rule 10

```text
Agent must be able to stop safely
```

---

## 7.87 Phase 7 Position in SIP

Ab overall architecture increasingly clear ho rahi hai:

```text
PHASE 1
Product Definition
        ↓
PHASE 2
System Architecture
        ↓
PHASE 3
Core RAG / Retrieval Intelligence
        ↓
PHASE 4
Data Layer & Knowledge Storage
        ↓
PHASE 5
Knowledge Ingestion & Crawling
        ↓
PHASE 6
Expert System & Expert Lifecycle
        ↓
PHASE 7
LLM Gateway + Tools + Agent Runtime
        ↓
PHASE 8+
Application / Orchestration / Evaluation / Deployment
```
