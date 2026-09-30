"""Tool Registry and Execution — M6 implementation.

Manages tool registration, input/output validation, permission enforcement,
and safe execution.
"""

from __future__ import annotations

import logging
import time

from jsonschema import ValidationError as JsonSchemaValidationError
from jsonschema import validate

from sip.core.contracts.tools import (
    Tool,
    ToolCall,
    ToolPermission,
    ToolResult,
    ToolStatus,
)
from sip.core.protocols.tools import ToolExecutor

logger = logging.getLogger(__name__)


class ToolRegistryManager:
    """Central registry and execution engine for tools."""

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}
        self._executors: dict[str, ToolExecutor] = {}

    def register(self, tool: Tool, executor: ToolExecutor) -> None:
        """Register a tool and its implementation."""
        if tool.id in self._tools:
            logger.warning("Overwriting existing tool registration: %s", tool.id)
        self._tools[tool.id] = tool
        self._executors[tool.id] = executor
        logger.info("Registered tool: %s (%s)", tool.name, tool.id)

    def get_tool(self, tool_id: str) -> Tool | None:
        """Get a tool definition by ID."""
        return self._tools.get(tool_id)

    def list_tools(self) -> list[Tool]:
        """List all registered tools."""
        return list(self._tools.values())

    async def execute(
        self,
        tool_call: ToolCall,
        granted_permissions: frozenset[ToolPermission],
    ) -> ToolResult:
        """Execute a tool call safely.

        Args:
            tool_call: The raw tool call from the LLM.
            granted_permissions: The permissions granted to the current agent context.

        Returns:
            A normalized ToolResult. Never raises an exception directly;
            errors are caught and returned as failed ToolResults.
        """
        start_time = time.perf_counter()

        def _make_result(
            status: ToolStatus,
            output: dict[str, object] | None = None,
            error_message: str | None = None,
        ) -> ToolResult:
            return ToolResult(
                tool_call_id=tool_call.id,
                tool_id=tool_call.tool_id,
                status=status,
                output=output,
                error_message=error_message,
                latency_ms=(time.perf_counter() - start_time) * 1000,
            )

        # 1. Lookup Tool
        tool = self.get_tool(tool_call.tool_id)
        if not tool:
            return _make_result(
                ToolStatus.FAILURE,
                error_message=f"Tool not found: {tool_call.tool_id}",
            )

        if not tool.is_active:
            return _make_result(
                ToolStatus.FAILURE,
                error_message=f"Tool is currently disabled: {tool.name}",
            )

        executor = self._executors.get(tool.id)
        if not executor:
            return _make_result(
                ToolStatus.FAILURE,
                error_message=f"No executor registered for tool: {tool.name}",
            )

        # 2. Permission Check
        missing_permissions = tool.required_permissions - granted_permissions
        if missing_permissions:
            return _make_result(
                ToolStatus.PERMISSION_DENIED,
                error_message=(
                    f"Permission denied. Tool requires: {list(missing_permissions)}. "
                    f"Context has: {list(granted_permissions)}"
                ),
            )

        # 3. Input Validation
        if tool.input_schema:
            try:
                validate(instance=tool_call.raw_input, schema=tool.input_schema)
            except JsonSchemaValidationError as e:
                return _make_result(
                    ToolStatus.INPUT_INVALID,
                    error_message=f"Input validation failed: {e.message}",
                )

        # 4. Execution
        try:
            output = await executor.execute(tool_call)
        except Exception as e:
            logger.exception("Tool execution failed: %s", tool.name)
            return _make_result(
                ToolStatus.FAILURE,
                error_message=f"Execution error: {e!s}",
            )

        # 5. Output Validation
        if tool.output_schema:
            try:
                validate(instance=output, schema=tool.output_schema)
            except JsonSchemaValidationError as e:
                logger.error("Tool output validation failed: %s", e.message)
                return _make_result(
                    ToolStatus.OUTPUT_INVALID,
                    error_message=f"Output validation failed: {e.message}",
                )

        # 6. Success
        return _make_result(ToolStatus.SUCCESS, output=output)
