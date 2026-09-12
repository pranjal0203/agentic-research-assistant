"""
Tool selector service.

This module determines which registered
tools are required to answer a question.

The planner is intentionally decoupled from
specific tools. Tool capabilities are supplied
dynamically from the tool registry.

The follow-up planner is evidence-aware:
retrieval relevance alone does not imply that
the user's question has been sufficiently answered.
"""

import json
import re
from datetime import datetime, timezone
from typing import Any

from groq import BadRequestError, RateLimitError
from langchain_core.messages import HumanMessage

from models.tool_call import ToolCall
from models.tool_result import ToolResult
from services.llm import llm
from services.tool_registry import (
    get_tool,
    list_tools,
)

# --------------------------------------------------
# Tool catalog
# --------------------------------------------------


def _build_tool_catalog() -> str:
    """
    Build the planner's tool catalog from
    the registered tools.

    No tool names are hardcoded here.
    """

    lines: list[str] = []

    for tool in list_tools():
        arguments = ", ".join(
            tool.arguments,
        )

        lines.append(
            "\n".join(
                (
                    f"Tool: {tool.name}",
                    f"Description: {tool.description}",
                    f"Arguments: {arguments}",
                    ("Selection guidance: " f"{tool.selection_hint}"),
                    f"Scope: {tool.scope}",
                    ("Requires current information: " f"{tool.requires_current}"),
                )
            )
        )

    return "\n\n".join(lines)


# --------------------------------------------------
# Current-question detection
# --------------------------------------------------


CURRENT_TERMS = (
    "current",
    "currently",
    "latest",
    "today",
    "now",
    "recent",
    "recently",
    "this year",
    "this month",
    "this week",
    "as of",
)

COMPARISON_TERMS = (
    "compare",
    "comparison",
    "compared",
    "versus",
    "vs",
    "difference",
    "differences",
    "better than",
    "different from",
)

CURRENT_STATE_TERMS = (
    "current state",
    "state of the art",
    "state-of-the-art",
    "current technology",
    "modern technology",
    "current approaches",
    "modern approaches",
    "current models",
    "modern models",
    "current methods",
    "modern methods",
    "today's",
    "today",
    "latest",
    "currently",
)


def _is_current_question(
    question: str,
) -> bool:
    """
    Determine whether the user explicitly
    requests current or time-sensitive
    information.

    This is only used as a safety constraint
    for current-only tools. It does not decide
    which specific tool should answer the
    question.
    """

    normalized = question.casefold()

    return any(term in normalized for term in CURRENT_TERMS)


def _is_comparison_with_current_state(
    question: str,
) -> bool:
    """
    Determine whether the question compares
    something with the current state of a field.

    This is intentionally generic and does not
    reference any specific model, technology,
    company, or domain.
    """

    normalized = question.casefold()

    has_comparison = any(term in normalized for term in COMPARISON_TERMS)

    has_current_state = any(term in normalized for term in CURRENT_STATE_TERMS)

    return has_comparison and has_current_state


def _build_current_query(
    question: str,
) -> str:
    """
    Build a concise, search-oriented query for
    tools that require current information.

    The query preserves the user's subject while
    adding generic retrieval dimensions for
    current-state research.
    """

    year = datetime.now(
        timezone.utc,
    ).year

    normalized = " ".join(
        question.strip().split(),
    )

    if _is_comparison_with_current_state(
        normalized,
    ):
        return (
            f"{normalized} {year} "
            "leading approaches "
            "current capabilities "
            "limitations "
            "benchmarks "
            "recent developments"
        )

    if str(year) in normalized:
        return normalized

    # Do not append the current year if a specific 4-digit year (e.g. 1900-2099) is already present
    if re.search(r"\b(19\d{2}|20\d{2})\b", normalized):
        return normalized

    return f"{normalized} {year}"


# --------------------------------------------------
# Planner response parsing
# --------------------------------------------------


def _response_to_text(
    response: Any,
) -> str:
    """
    Convert an LLM response into plain text.
    """

    content = getattr(
        response,
        "content",
        response,
    )

    if isinstance(
        content,
        str,
    ):
        return content

    if isinstance(
        content,
        list,
    ):
        parts: list[str] = []

        for item in content:
            if isinstance(
                item,
                str,
            ):
                parts.append(item)

            elif isinstance(
                item,
                dict,
            ):
                text = item.get(
                    "text",
                )

                if text:
                    parts.append(
                        str(text),
                    )

        return "".join(parts)

    return str(content)


def _extract_json(
    text: str,
) -> dict[str, Any] | None:
    """
    Extract a JSON object from planner output.

    The model may occasionally wrap JSON in
    markdown fences, so parsing is intentionally
    tolerant.
    """

    text = text.strip()

    if not text:
        return None

    try:
        parsed = json.loads(
            text,
        )

        if isinstance(
            parsed,
            dict,
        ):
            return parsed

    except json.JSONDecodeError:
        pass

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        return None

    if end <= start:
        return None

    candidate = text[start : end + 1]

    try:
        parsed = json.loads(
            candidate,
        )

    except json.JSONDecodeError:
        return None

    if not isinstance(
        parsed,
        dict,
    ):
        return None

    return parsed


# --------------------------------------------------
# Tool call validation
# --------------------------------------------------


def _convert_tool_calls(
    raw_calls: Any,
) -> tuple[ToolCall, ...]:
    """
    Convert planner JSON into validated
    application ToolCall objects.

    Unknown tools, malformed arguments,
    and incomplete calls are rejected.
    """

    if not isinstance(
        raw_calls,
        list,
    ):
        return ()

    calls: list[ToolCall] = []

    for raw_call in raw_calls:
        if not isinstance(
            raw_call,
            dict,
        ):
            continue

        tool_name = raw_call.get(
            "tool",
        )

        if not isinstance(
            tool_name,
            str,
        ):
            continue

        tool = get_tool(
            tool_name.strip(),
        )

        if tool is None:
            continue

        arguments = raw_call.get(
            "arguments",
        )

        if not isinstance(
            arguments,
            dict,
        ):
            continue

        normalized_arguments: dict[str, Any] = {}

        valid = True

        for argument_name in tool.arguments:
            if argument_name not in arguments:
                valid = False
                break

            value = arguments[argument_name]

            if value is None:
                valid = False
                break

            if isinstance(
                value,
                str,
            ):
                value = value.strip()

                if not value:
                    valid = False
                    break

            normalized_arguments[argument_name] = value

        if not valid:
            continue

        calls.append(
            ToolCall(
                tool=tool,
                arguments=normalized_arguments,
            )
        )

    return tuple(calls)


# --------------------------------------------------
# Current-query normalization
# --------------------------------------------------


def _normalize_current_tool_queries(
    question: str,
    tool_calls: tuple[ToolCall, ...],
) -> tuple[ToolCall, ...]:
    """
    Improve queries for tools that explicitly
    require current information.

    This operates entirely on Tool metadata.

    No specific Web tool or search provider
    is referenced here.
    """

    normalized_calls: list[ToolCall] = []

    for tool_call in tool_calls:
        if not tool_call.tool.requires_current:
            normalized_calls.append(
                tool_call,
            )
            continue

        arguments = dict(
            tool_call.arguments,
        )

        if "query" not in arguments:
            normalized_calls.append(
                tool_call,
            )
            continue

        query = str(
            arguments["query"],
        ).strip()

        if not query:
            normalized_calls.append(
                tool_call,
            )
            continue

        if _is_comparison_with_current_state(
            question,
        ):
            query = _build_current_query(
                question,
            )

        else:
            query = _build_current_query(
                query,
            )

        normalized_calls.append(
            ToolCall(
                tool=tool_call.tool,
                arguments={
                    **arguments,
                    "query": query,
                },
            )
        )

    return tuple(normalized_calls)


# --------------------------------------------------
# Fallback routing
# --------------------------------------------------


def _default_tool_call(
    question: str,
) -> tuple[ToolCall, ...]:
    """
    Provide a safe registry-driven fallback.

    The fallback never assumes that a particular
    tool name is the default local tool.
    """

    tools = list_tools()

    current_tools = [tool for tool in tools if tool.default_for_current]

    local_tools = [tool for tool in tools if tool.default_for_local]

    if _is_current_question(
        question,
    ):
        if current_tools:
            tool = current_tools[0]

        elif local_tools:
            tool = local_tools[0]

        else:
            return ()

    else:
        if local_tools:
            tool = local_tools[0]

        elif tools:
            tool = tools[0]

        else:
            return ()

    if tool.arguments != ("query",):
        return ()

    query = question

    if tool.requires_current:
        query = _build_current_query(
            question,
        )

    return (
        ToolCall(
            tool=tool,
            arguments={
                "query": query,
            },
        ),
    )


# --------------------------------------------------
# Current-only safety filtering
# --------------------------------------------------


def _filter_unnecessary_current_tools(
    question: str,
    tool_calls: tuple[ToolCall, ...],
) -> tuple[ToolCall, ...]:
    """
    Prevent current-only tools from being used
    as supplementary searches when the question
    does not ask for current information and a
    local tool already covers the question.

    This is deliberately generic and operates
    on Tool metadata rather than tool names.
    """

    if _is_current_question(
        question,
    ):
        return tool_calls

    has_local_tool = any(call.tool.scope == "local" for call in tool_calls)

    if not has_local_tool:
        return tool_calls

    return tuple(call for call in tool_calls if not call.tool.requires_current)


# --------------------------------------------------
# Initial planning
# --------------------------------------------------


def select_tool_calls(
    question: str,
    collection_name: str | None = None,
    source_files: list[str] | None = None,
) -> tuple[ToolCall, ...]:
    """
    Select the minimum set of registered tools
    required to answer a question.
    """

    question = question.strip()

    if not question:
        return ()

    catalog = _build_tool_catalog()

    collection_context = ""
    if collection_name:
        files_str = (
            "\n".join(f"- {f}" for f in source_files)
            if source_files
            else "- No files listed"
        )
        collection_context = f"\nACTIVE DOCUMENT COLLECTION:\n- Collection name: {collection_name}\n- Available local documents:\n{files_str}\n"

    prompt = f"""
You are the planning component of an agentic research assistant. Decide which registered tools are required to retrieve evidence for the user's question. Do NOT answer the question.

TOOL CATALOG:
{catalog}
{collection_context}
ROUTING PRINCIPLES:
1. Select the minimum number of tools needed.
2. Prefer local tools for information expected to be in the local database or local documents listed above.
3. Use web/external tools ONLY if the question explicitly asks for current information (e.g., latest, recent, now, future dates like 2025/2026) OR is external/unrelated to the local documents listed above.
4. Do not return duplicate calls. Make queries specific and self-contained.

OUTPUT FORMAT:
Return ONLY valid JSON using exactly this structure:
{{
  "tool_calls": [
    {{
      "tool": "registered_tool_name",
      "arguments": {{
        "argument_name": "argument_value"
      }}
    }}
  ]
}}

USER QUESTION:
{question}
"""

    try:
        response = llm.invoke(
            [
                HumanMessage(
                    content=prompt,
                ),
            ],
        )

    except (BadRequestError, RateLimitError):
        return _default_tool_call(
            question,
        )

    parsed = _extract_json(
        _response_to_text(
            response,
        )
    )

    if parsed is None:
        return _default_tool_call(
            question,
        )

    tool_calls = _convert_tool_calls(
        parsed.get(
            "tool_calls",
            [],
        )
    )

    tool_calls = _normalize_current_tool_queries(
        question,
        tool_calls,
    )

    tool_calls = _filter_unnecessary_current_tools(
        question,
        tool_calls,
    )

    if not tool_calls:
        return _default_tool_call(
            question,
        )

    return tool_calls


# --------------------------------------------------
# Follow-up planning
# --------------------------------------------------


def _format_observations(
    tool_results: tuple[ToolResult, ...],
) -> str:
    """
    Format previous tool results for the
    follow-up planner.
    """

    if not tool_results:
        return "No previous tool results."

    blocks: list[str] = []

    for index, result in enumerate(
        tool_results,
        start=1,
    ):
        blocks.append(
            "\n".join(
                (
                    f"Result {index}",
                    f"Tool: {result.tool.name}",
                    f"Arguments: {result.arguments}",
                    ("Relevant content: " f"{result.has_relevant_content}"),
                    ("Observation:\n" f"{result.observation}"),
                )
            )
        )

    return "\n\n".join(
        blocks,
    )


# --------------------------------------------------
# Follow-up planning
# --------------------------------------------------


def select_follow_up_tool_calls(
    question: str,
    tool_results: tuple[ToolResult, ...],
    collection_name: str | None = None,
    source_files: list[str] | None = None,
) -> tuple[ToolCall, ...]:
    """
    Decide whether additional retrieval is needed.

    Retrieval relevance is NOT treated as evidence
    sufficiency.

    The planner evaluates whether the available
    observations actually contain enough information
    to answer the user's question.

    At most one additional retrieval call is
    requested from this function.
    """

    if not tool_results:
        return ()

    catalog = _build_tool_catalog()

    observations = _format_observations(
        tool_results,
    )

    collection_context = ""
    if collection_name:
        files_str = (
            "\n".join(f"- {f}" for f in source_files)
            if source_files
            else "- No files listed"
        )
        collection_context = f"\nACTIVE DOCUMENT COLLECTION:\n- Collection name: {collection_name}\n- Available local documents:\n{files_str}\n"

    prompt = f"""
You are the evidence-sufficiency component of an agentic research assistant. Decide whether the retrieved evidence is sufficient to answer the question directly. Do NOT answer the question.

TOOL CATALOG:
{catalog}
{collection_context}
DECISION RULES:
1. If the evidence directly and sufficiently supports the answer, return an empty tool_calls list.
2. Do NOT use current-only/web tools (like search_web) unless the question actually requires current or external information (e.g. latest, recent, now, future dates like 2025/2026) AND the local documents do not contain it.
3. If the evidence is relevant but incomplete/partial, request ONE additional retrieval tool call. Make the follow-up query more specific to target the missing details.
4. If another retrieval is unlikely to produce meaningful improvement, return an empty list.
5. Use only registered tools. Make at most ONE tool call. Never repeat an identical tool call.

OUTPUT FORMAT:
Return ONLY valid JSON.
If evidence is sufficient:
{{
  "tool_calls": []
}}
If another retrieval is justified:
{{
  "tool_calls": [
    {{
      "tool": "registered_tool_name",
      "arguments": {{
        "argument_name": "more_specific_query"
      }}
    }}
  ]
}}

USER QUESTION:
{question}

RETRIEVED EVIDENCE:
{observations}
"""

    try:
        response = llm.invoke(
            [
                HumanMessage(
                    content=prompt,
                ),
            ],
        )

    except (BadRequestError, RateLimitError):
        return ()

    parsed = _extract_json(
        _response_to_text(
            response,
        )
    )

    if parsed is None:
        return ()

    tool_calls = _convert_tool_calls(
        parsed.get(
            "tool_calls",
            [],
        )
    )

    tool_calls = _normalize_current_tool_queries(
        question,
        tool_calls,
    )

    tool_calls = _filter_unnecessary_current_tools(
        question,
        tool_calls,
    )

    return tool_calls[:1]
