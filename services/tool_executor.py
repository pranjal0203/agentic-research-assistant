"""
Tool executor service.

This module executes tool calls created
by the AI agent.

The agent itself does not know how a tool
is implemented. Execution is resolved here.
"""

from collections.abc import Callable

from models.tool import Tool
from models.tool_call import ToolCall
from models.tool_result import ToolResult
from models.tool_runtime import ToolRuntime
from services.tool_registry import (
    SEARCH_PDF_TOOL,
    SEARCH_WEB_TOOL,
)
from services.tools.pdf_tool import (
    execute_pdf_tool,
)
from services.tools.web_tool import (
    execute_web_tool,
)

ToolExecutor = Callable[
    [ToolCall, ToolRuntime],
    ToolResult,
]


# --------------------------------------------------
# Executor registry
# --------------------------------------------------


TOOL_EXECUTORS: dict[
    Tool,
    ToolExecutor,
] = {
    SEARCH_PDF_TOOL: execute_pdf_tool,
    SEARCH_WEB_TOOL: execute_web_tool,
}


def register_tool_executor(
    tool: Tool,
    executor: ToolExecutor,
) -> None:
    """
    Register an executor for a tool.

    This function allows future tools to be
    registered without changing agent logic.
    """

    TOOL_EXECUTORS[tool] = executor


def get_tool_executor(
    tool: Tool,
) -> ToolExecutor | None:
    """
    Return the executor registered for a tool.
    """

    return TOOL_EXECUTORS.get(
        tool,
    )


def execute_tool(
    tool_call: ToolCall,
    runtime: ToolRuntime,
) -> ToolResult:
    """
    Execute a tool call.

    Tool failures are converted into
    ToolResult objects so the agent can
    observe the failure.

    Args:
        tool_call:
            Requested tool invocation.

        runtime:
            Runtime resources available
            to the tool.

    Returns:
        Tool execution result.

    Raises:
        ValueError:
            If no executor is registered
            for the requested tool.
    """

    executor = get_tool_executor(
        tool_call.tool,
    )

    if executor is None:
        raise ValueError(
            f"Unknown tool: '{tool_call.tool.name}'.",
        )

    try:
        return executor(
            tool_call,
            runtime,
        )

    except (
        RuntimeError,
        ValueError,
        OSError,
    ) as error:
        return ToolResult(
            tool=tool_call.tool,
            arguments=tool_call.arguments,
            success=False,
            error=str(error),
        )
