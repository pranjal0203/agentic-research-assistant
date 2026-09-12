"""
Agent state model.

Represents the current state of
the AI agent while answering a
question.
"""

from dataclasses import dataclass

from config.settings import MAX_AGENT_ITERATIONS
from models.tool_call import ToolCall
from models.tool_result import ToolResult


@dataclass(slots=True)
class AgentState:
    """
    Current state of the AI agent.
    """

    question: str

    tool_calls: tuple[ToolCall, ...] = ()

    tool_results: tuple[ToolResult, ...] = ()

    iterations: int = 0

    max_iterations: int = MAX_AGENT_ITERATIONS

    final_answer: str | None = None

    def can_continue(self) -> bool:
        """
        Return whether the agent may
        execute another reasoning step.
        """

        return self.iterations < self.max_iterations

    def advance(self) -> None:
        """
        Advance the agent iteration count.
        """

        self.iterations += 1
