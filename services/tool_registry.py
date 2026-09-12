"""
Tool registry service.

This module defines the capabilities
available to the AI agent.

The planner should discover tools from
this registry rather than maintaining its
own hardcoded list.
"""

from models.tool import Tool

# --------------------------------------------------
# Local knowledge tool
# --------------------------------------------------

SEARCH_PDF_TOOL = Tool(
    name="search_pdf",
    description=(
        "Search the local indexed knowledge base "
        "for information contained in the user's "
        "document collection."
    ),
    arguments=("query",),
    selection_hint=(
        "Use for concepts, definitions, facts, "
        "methods, architectures, findings, papers, "
        "and other information that may be contained "
        "in the local documents."
    ),
    scope="local",
    requires_current=False,
    default_for_local=True,
)


# --------------------------------------------------
# Web knowledge tool
# --------------------------------------------------

SEARCH_WEB_TOOL = Tool(
    name="search_web",
    description=(
        "Search the internet for information that "
        "is current, external, time-sensitive, or "
        "not expected to be available in the local "
        "knowledge base."
    ),
    arguments=("query",),
    selection_hint=(
        "Use when the user explicitly needs current, "
        "latest, recent, today's, now, or external "
        "internet information. Do not use merely "
        "because web confirmation would be useful."
    ),
    scope="web",
    requires_current=True,
    default_for_current=True,
)


# --------------------------------------------------
# Registry
# --------------------------------------------------

TOOLS: tuple[Tool, ...] = (
    SEARCH_PDF_TOOL,
    SEARCH_WEB_TOOL,
)


def list_tools() -> tuple[Tool, ...]:
    """
    Return all registered tools.
    """

    return TOOLS


def get_tool(
    name: str,
) -> Tool | None:
    """
    Return a registered tool by name.
    """

    normalized_name = name.strip()

    for tool in TOOLS:
        if tool.name == normalized_name:
            return tool

    return None
