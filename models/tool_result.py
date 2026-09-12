"""
Tool result model.

Represents the result produced after
the AI agent executes a tool.

The model also provides a bounded observation
representation for agent planning so large
retrieval results do not consume the entire
LLM context budget.
"""

from dataclasses import dataclass
from typing import Any

from config.settings import (
    FOLLOW_UP_OBSERVATION_MAX_CHARS,
    FOLLOW_UP_OBSERVATION_TOP_K,
)
from models.knowledge import Knowledge
from models.tool import Tool


@dataclass(slots=True, frozen=True)
class ToolResult:
    """
    Result produced by a tool execution.
    """

    tool: Tool

    arguments: dict[str, Any]

    knowledge: Knowledge | None = None

    success: bool = True

    error: str | None = None

    @property
    def has_relevant_content(self) -> bool:
        """
        Return whether the tool produced
        usable retrieval content.
        """

        if not self.success:
            return False

        if self.knowledge is None:
            return False

        return any(
            candidate.content.strip()
            for candidate in self.knowledge.candidates
            if candidate.content
        )

    @staticmethod
    def _truncate_content(
        content: str,
    ) -> str:
        """
        Bound an individual evidence block
        used by the follow-up planner.
        """

        content = content.strip()

        if len(content) <= FOLLOW_UP_OBSERVATION_MAX_CHARS:
            return content

        return (
            content[:FOLLOW_UP_OBSERVATION_MAX_CHARS].rstrip()
            + "\n[Evidence truncated.]"
        )

    @property
    def observation(self) -> str:
        """
        Convert the tool result into a bounded
        textual observation for agent planning.

        Only the strongest retrieved candidates
        are exposed and each candidate is bounded
        by a configurable character limit.

        The complete retrieval result remains
        available through ``knowledge``.
        """

        if not self.success:
            return (
                f"Tool '{self.tool.name}' failed. "
                f"Error: {self.error or 'Unknown error.'}"
            )

        if self.knowledge is None:
            return (
                f"Tool '{self.tool.name}' completed "
                "successfully but returned no knowledge."
            )

        candidates = [
            candidate
            for candidate in self.knowledge.candidates
            if candidate.content and candidate.content.strip()
        ]

        if not candidates:
            return (
                f"Tool '{self.tool.name}' completed "
                "successfully but returned no relevant "
                "content."
            )

        observation_blocks: list[str] = []

        for index, candidate in enumerate(
            candidates[:FOLLOW_UP_OBSERVATION_TOP_K],
            start=1,
        ):
            content = self._truncate_content(
                candidate.content,
            )

            if not content:
                continue

            citation = candidate.citation

            source = candidate.source.value

            citation_parts = [
                source,
                citation.title,
                citation.location,
            ]

            citation_header = " | ".join(part for part in citation_parts if part)

            observation_blocks.append(
                "\n".join(
                    (
                        f"Evidence {index}",
                        f"Source: {citation_header}",
                        f"Score: {candidate.score:.4f}",
                        f"Content:\n{content}",
                    )
                )
            )

        if not observation_blocks:
            return (
                f"Tool '{self.tool.name}' completed "
                "successfully but returned no relevant "
                "content."
            )

        return "\n\n".join(
            observation_blocks,
        )
