"""
Agent planner service.

This module converts LLM-generated
tool calls into executable ToolCall
objects and creates follow-up tool
calls from tool observations.
"""

from models.tool_call import ToolCall
from models.tool_result import ToolResult
from services.tool_selector import (
    select_follow_up_tool_calls,
    select_tool_calls,
)


def create_tool_calls(
    question: str,
    collection_name: str | None = None,
    source_files: list[str] | None = None,
) -> tuple[ToolCall, ...]:
    """
    Create initial tool calls from the
    language model.

    Args:
        question:
            User question.

    Returns:
        Planned tool calls.
    """

    return select_tool_calls(
        question,
        collection_name=collection_name,
        source_files=source_files,
    )


def create_follow_up_tool_calls(
    question: str,
    tool_results: tuple[ToolResult, ...],
    collection_name: str | None = None,
    source_files: list[str] | None = None,
) -> tuple[ToolCall, ...]:
    """
    Create follow-up tool calls based on
    observations from previously executed
    tools.

    Args:
        question:
            Original user question.

        tool_results:
            Results produced by previously
            executed tools.

    Returns:
        Additional tool calls selected by
        the language model.
    """

    return select_follow_up_tool_calls(
        question,
        tool_results,
        collection_name=collection_name,
        source_files=source_files,
    )
