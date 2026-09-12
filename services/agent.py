"""
Agent service.

This module orchestrates question answering
for the AI agent.

Conversation-aware question rewriting is handled
by ConversationService before this module is called.

The agent therefore operates only on standalone
questions.
"""

from langchain_chroma import Chroma

from config.settings import (
    MAX_TOOL_EXECUTIONS_PER_RUN,
)
from models.agent_state import AgentState
from models.response import Response
from models.tool_call import ToolCall
from models.tool_result import ToolResult
from models.tool_runtime import ToolRuntime
from services.agent_planner import (
    create_follow_up_tool_calls,
    create_tool_calls,
)
from services.response_builder import (
    build_response,
)
from services.tool_executor import (
    execute_tool,
)


def _is_duplicate_tool_call(
    tool_call: ToolCall,
    tool_results: tuple[ToolResult, ...],
) -> bool:
    """
    Return whether an identical tool call
    has already been executed.
    """

    return any(
        (tool_call.tool == result.tool and tool_call.arguments == result.arguments)
        for result in tool_results
    )


def _has_reached_tool_limit(
    tool_call: ToolCall,
    tool_results: tuple[ToolResult, ...],
) -> bool:
    """
    Return whether this tool has reached
    its per-tool execution budget.
    """

    execution_count = sum(result.tool == tool_call.tool for result in tool_results)

    return execution_count >= MAX_TOOL_EXECUTIONS_PER_RUN


def _filter_tool_calls(
    tool_calls: tuple[ToolCall, ...],
    tool_results: tuple[ToolResult, ...],
) -> tuple[ToolCall, ...]:
    """
    Keep only eligible tool calls.

    A call is eligible when:

    - it is not an exact duplicate
    - its tool has not reached its execution limit
    """

    return tuple(
        tool_call
        for tool_call in tool_calls
        if (
            not _is_duplicate_tool_call(
                tool_call,
                tool_results,
            )
            and not _has_reached_tool_limit(
                tool_call,
                tool_results,
            )
        )
    )


def _format_arguments(
    arguments: dict,
) -> str:
    """
    Format arbitrary tool arguments for tracing.
    """

    if not arguments:
        return ""

    parts = [f"{key}={value!r}" for key, value in arguments.items()]

    return ", ".join(parts)


def _format_tool_call(
    tool_call: ToolCall,
) -> str:
    """
    Format a tool call for agent tracing.
    """

    arguments = _format_arguments(
        tool_call.arguments,
    )

    if arguments:
        return f"{tool_call.tool.name}" f"({arguments})"

    return tool_call.tool.name


def _format_tool_result(
    result: ToolResult,
) -> str:
    """
    Format a tool result for agent tracing.
    """

    arguments = _format_arguments(
        result.arguments,
    )

    if arguments:
        return f"{result.tool.name}" f"({arguments})"

    return result.tool.name


def answer_question(
    vector_store: Chroma,
    question: str,
) -> Response:
    """
    Answer a standalone question using
    the agentic retrieval workflow.

    Workflow:

        1. create initial retrieval plan
        2. execute selected tools
        3. store results
        4. request follow-up retrieval if necessary
        5. filter duplicate/budget-exceeded calls
        6. build final grounded response
    """

    question = question.strip()

    if not question:
        return Response.empty()

    import logging
    import os

    logger = logging.getLogger(__name__)
    collection_name = None
    source_files = []
    try:
        persist_dir = vector_store._client.get_settings().persist_directory
        if persist_dir:
            collection_name = os.path.basename(persist_dir)
            data_path = os.path.join("data", collection_name)
            if os.path.isdir(data_path):
                source_files = sorted(
                    [f for f in os.listdir(data_path) if not f.startswith(".")]
                )
    except (AttributeError, OSError) as e:
        logger.warning("Could not extract collection metadata: %s", e)

    state = AgentState(
        question=question,
    )

    runtime = ToolRuntime(
        vector_store=vector_store,
    )

    # --------------------------------------------------
    # Initial planning
    # --------------------------------------------------

    state.tool_calls = create_tool_calls(
        state.question,
        collection_name=collection_name,
        source_files=source_files,
    )

    state.tool_calls = _filter_tool_calls(
        state.tool_calls,
        state.tool_results,
    )

    print(
        "[Agent] Initial tools:",
        [
            _format_tool_call(
                tool_call,
            )
            for tool_call in state.tool_calls
        ],
    )

    # --------------------------------------------------
    # Agent execution loop
    # --------------------------------------------------

    while state.tool_calls and state.can_continue():

        current_results = tuple(
            execute_tool(
                tool_call,
                runtime,
            )
            for tool_call in state.tool_calls
        )

        state.tool_results = state.tool_results + current_results

        print(
            "[Agent] Observations:",
            [
                _format_tool_result(
                    result,
                )
                for result in current_results
            ],
        )

        state.advance()

        if not state.can_continue():
            state.tool_calls = ()
            break

        next_tool_calls = create_follow_up_tool_calls(
            question=state.question,
            tool_results=state.tool_results,
            collection_name=collection_name,
            source_files=source_files,
        )

        state.tool_calls = _filter_tool_calls(
            next_tool_calls,
            state.tool_results,
        )

        print(
            "[Agent] Follow-up tools:",
            [
                _format_tool_call(
                    tool_call,
                )
                for tool_call in state.tool_calls
            ],
        )

    # --------------------------------------------------
    # Stop reason
    # --------------------------------------------------

    if not state.tool_calls:
        print(
            "[Agent] Stopped: no eligible " "follow-up tools.",
        )

    elif not state.can_continue():
        print(
            "[Agent] Stopped: maximum " "iteration limit reached.",
        )

    # --------------------------------------------------
    # Final grounded response
    # --------------------------------------------------

    return build_response(
        question=state.question,
        tool_results=state.tool_results,
    )
