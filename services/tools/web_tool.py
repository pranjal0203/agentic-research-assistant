"""
Web tool service.

Executes web searches for
the AI agent.
"""

from models.tool_call import ToolCall
from models.tool_result import ToolResult
from models.tool_runtime import ToolRuntime
from services.knowledge.web import search_web_knowledge


def execute_web_tool(
    tool_call: ToolCall,
    runtime: ToolRuntime,
) -> ToolResult:
    """
    Execute a web search.
    """

    _ = runtime

    knowledge = search_web_knowledge(
        tool_call.query,
    )

    return ToolResult(
        tool=tool_call.tool,
        arguments=tool_call.arguments,
        knowledge=knowledge,
    )
