"""Tool System protocols — M6 requirements.

These protocols abstract tool registration and execution.
"""

from typing import Protocol

from sip.core.contracts.tools import Tool, ToolCall, ToolResult

class ToolExecutor(Protocol):
    """Protocol for an individual tool's executor implementation.

    The executor is responsible for taking validated input and returning
    output matching the tool's output schema.
    """

    async def execute(self, tool_call: ToolCall) -> dict[str, object]:
        """Execute the tool logic.

        Args:
            tool_call: The tool call with pre-validated arguments.

        Returns:
            A dictionary matching the tool's output schema.

        Raises:
            Exception: If execution fails. The runtime will catch this
                and translate it to a ToolStatus.FAILURE ToolResult.
        """
        ...

class ToolRegistry(Protocol):
    """Protocol for the central Tool Registry.

    Manages available tools, schema validation, and permissions.
    """

    def register(self, tool: Tool, executor: ToolExecutor) -> None:
        """Register a tool and its executor implementation."""
        ...

    def get_tool(self, tool_id: str) -> Tool | None:
        """Get a tool definition by ID."""
        ...

    async def execute(self, tool_call: ToolCall) -> ToolResult:
        """Execute a tool call safely.

        The registry is responsible for validating the input schema,
        invoking the bound executor, catching exceptions, validating the
        output schema, and returning a normalized ToolResult.
        """
        ...
