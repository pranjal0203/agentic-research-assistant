"""
Tool model.

Represents a capability that can be
invoked by the AI agent.
"""

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class Tool:
    """
    Represents a capability that can
    be invoked by the AI agent.

    Tool metadata is intentionally kept
    independent from the agent planner.

    This allows new tools to be added to
    the registry without changing the
    planner's routing logic.
    """

    name: str
    description: str

    # Names of arguments expected by the tool.
    #
    # Most retrieval tools use:
    #     ("query",)
    #
    # Future tools may define different
    # arguments, for example:
    #
    #     ("expression",)
    #
    # or:
    #
    #     ("query", "limit")
    arguments: tuple[str, ...] = ("query",)

    # Additional guidance shown to the
    # planning model.
    selection_hint: str = ""

    # Logical scope of the tool.
    #
    # Examples:
    #     local
    #     web
    #     external
    #     computation
    #     database
    scope: str = "external"

    # If True, the tool should only be selected
    # when the question explicitly requires
    # current/time-sensitive information.
    requires_current: bool = False

    # Used only for safe fallback routing.
    default_for_local: bool = False
    default_for_current: bool = False
