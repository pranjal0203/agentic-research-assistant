"""
Tool runtime model.

Represents runtime resources
available to tool execution.
"""

from dataclasses import dataclass

from langchain_chroma import Chroma


@dataclass(slots=True, frozen=True)
class ToolRuntime:
    """
    Runtime resources shared by
    tool implementations.
    """

    vector_store: Chroma
