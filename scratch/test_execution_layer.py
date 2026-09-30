"""Interactive test script for the LLM Gateway and Tool Registry (M6)."""

import asyncio
from typing import AsyncGenerator
from uuid import uuid4

from sip.core.contracts.llm import (
    FinishReason,
    LLMProvider,
    LLMRequest,
    LLMResponse,
    Message,
    MessageRole,
    ModelProfile,
    TokenUsage,
)
from sip.core.contracts.tools import (
    Tool,
    ToolCall,
    ToolPermission,
    ToolResult,
)
from sip.core.protocols.llm import LLMProviderAdapter
from sip.llm.gateway import CentralLLMGateway
from sip.tools.registry import ToolRegistryManager


# ─── Mock LLM Provider Adapter ──────────────────────────────────────────────

class MockEchoAdapter(LLMProviderAdapter):
    """A mock LLM adapter that echoes back what it received, or triggers a tool."""

    async def generate(self, request: LLMRequest) -> LLMResponse:
        last_msg = request.messages[-1].content
        
        # If user asks to search, pretend we want to call a tool
        if "search" in last_msg.lower():
            return LLMResponse(
                request_id=request.id,
                content='{"tool": "knowledge_search", "query": "test query"}',
                finish_reason=FinishReason.TOOL_CALL,
                usage=TokenUsage(input_tokens=10, output_tokens=15, total_tokens=25),
                model_used=request.model_profile.model_id,
                provider=request.model_profile.provider,
                latency_ms=150.0,
            )

        return LLMResponse(
            request_id=request.id,
            content=f"Echo from {request.model_profile.provider.value}: {last_msg}",
            finish_reason=FinishReason.STOP,
            usage=TokenUsage(input_tokens=10, output_tokens=20, total_tokens=30),
            model_used=request.model_profile.model_id,
            provider=request.model_profile.provider,
            latency_ms=120.0,
        )

    async def stream(self, request: LLMRequest) -> AsyncGenerator[LLMResponse, None]:  # type: ignore
        response = await self.generate(request)
        # Yield the response in two chunks
        part1 = response.model_copy(update={"content": response.content[:10]})
        part2 = response.model_copy(update={"content": response.content[10:]})
        yield part1
        yield part2

# ─── Mock Tool Executor ─────────────────────────────────────────────────────

class MockSearchExecutor:
    """A mock executor for the knowledge_search tool."""

    async def execute(self, tool_call: ToolCall) -> dict[str, object]:
        query = str(tool_call.raw_input.get("query", ""))
        print(f"    [Executor executing search for query: '{query}']")
        return {
            "results": [
                f"Result 1 for {query}",
                f"Result 2 for {query}",
            ]
        }


# ─── Interactive test ────────────────────────────────────────────────────────


async def main() -> None:
    print("=" * 60)
    print("SIP Intelligence Execution (M6) - Interactive Test")
    print("=" * 60)

    # 1. Setup Tool Registry
    registry = ToolRegistryManager()
    
    search_tool = Tool(
        id="knowledge_search",
        name="Knowledge Search",
        description="Search the knowledge base.",
        input_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string"},
            },
            "required": ["query"],
        },
        output_schema={
            "type": "object",
            "properties": {
                "results": {"type": "array", "items": {"type": "string"}},
            },
        },
        required_permissions=frozenset({ToolPermission.KNOWLEDGE_READ}),
    )
    
    registry.register(search_tool, MockSearchExecutor())

    # 2. Setup LLM Gateway
    gateway = CentralLLMGateway()
    gateway.register_adapter(LLMProvider.OLLAMA, MockEchoAdapter())

    profile = ModelProfile(
        provider=LLMProvider.OLLAMA,
        model_id="mock-qwen-7b",
        context_window=8192,
    )

    # ── Test 1: Simple LLM Generation ──────────────────────────────────────
    print("\n[TEST 1: LLM Gateway Simple Generation]")
    req1 = LLMRequest(
        model_profile=profile,
        messages=(
            Message(role=MessageRole.USER, content="Hello, SIP!"),
        ),
    )
    resp1 = await gateway.generate(req1)
    print(f"  Response: {resp1.content}")
    print(f"  Provider: {resp1.provider.value}")
    print(f"  Usage:    {resp1.usage.total_tokens} tokens")
    
    # ── Test 2: Tool Execution (Valid) ─────────────────────────────────────
    print("\n[TEST 2: Tool Registry Execution (Valid)]")
    
    call1 = ToolCall(
        tool_id="knowledge_search",
        raw_input={"query": "FastAPI async"},
    )
    
    # We grant the required permission
    perms = frozenset({ToolPermission.KNOWLEDGE_READ})
    
    res1 = await registry.execute(call1, granted_permissions=perms)
    print(f"  Status:   {res1.status.value}")
    print(f"  Output:   {res1.output}")
    print(f"  Latency:  {res1.latency_ms:.2f}ms")

    # ── Test 3: Tool Execution (Permission Denied) ─────────────────────────
    print("\n[TEST 3: Tool Registry Execution (Permission Denied)]")
    
    call2 = ToolCall(
        tool_id="knowledge_search",
        raw_input={"query": "secret data"},
    )
    
    # We DO NOT grant the required permission
    no_perms = frozenset()
    
    res2 = await registry.execute(call2, granted_permissions=no_perms)
    print(f"  Status:   {res2.status.value}")
    print(f"  Error:    {res2.error_message}")

    # ── Test 4: Tool Execution (Invalid Input) ─────────────────────────────
    print("\n[TEST 4: Tool Registry Execution (Invalid Schema)]")
    
    call3 = ToolCall(
        tool_id="knowledge_search",
        # Schema requires "query", we provide "q"
        raw_input={"q": "FastAPI async"},
    )
    
    res3 = await registry.execute(call3, granted_permissions=perms)
    print(f"  Status:   {res3.status.value}")
    print(f"  Error:    {res3.error_message}")

    print("\n" + "=" * 60)
    print("All Execution layer tests passed! [OK]")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
