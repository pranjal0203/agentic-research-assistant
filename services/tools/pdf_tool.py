"""
PDF tool service.

Executes PDF searches for
the AI agent.
"""

from models.tool_call import ToolCall
from models.tool_result import ToolResult
from models.tool_runtime import ToolRuntime
from services.knowledge.pdf import (
    search_pdf_knowledge,
)


def execute_pdf_tool(
    tool_call: ToolCall,
    runtime: ToolRuntime,
) -> ToolResult:
    """
    Execute a PDF search.

    Args:
        tool_call:
            Tool invocation requested
            by the AI agent.

        runtime:
            Runtime resources available
            to tool execution.

    Returns:
        Tool execution result.
    """

    knowledge = search_pdf_knowledge(
        runtime.vector_store,
        tool_call.query,
    )

    return ToolResult(
        tool=tool_call.tool,
        arguments=tool_call.arguments,
        knowledge=knowledge,
    )
