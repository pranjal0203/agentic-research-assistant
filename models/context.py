"""
Context model.

Represents the information
returned by a tool.
"""

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class Context:
    """
    Represents contextual information
    returned by a tool.
    """

    content: str
