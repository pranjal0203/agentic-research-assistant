from unittest.mock import MagicMock, patch

from models.confidence import Confidence
from models.response import Response
from models.source import Source
from models.tool_call import ToolCall
from models.tool_result import ToolResult
from services.agent import answer_question


@patch("services.agent.create_follow_up_tool_calls")
@patch("services.agent.create_tool_calls")
@patch("services.agent.execute_tool")
@patch("services.agent.build_response")
def test_answer_question_loop(mock_build, mock_execute, mock_create, mock_follow_up):
    """
    Verify the agent ReAct loop handles planning, execution, and response steps.
    """
    # Mock planning to return one tool call
    mock_tool = MagicMock()
    mock_tool.name = "search_pdf"
    mock_tool_call = ToolCall(tool=mock_tool, arguments={"query": "test"})
    mock_create.return_value = (mock_tool_call,)
    mock_follow_up.return_value = ()

    from models.knowledge import PDFKnowledge

    # Mock tool execution
    mock_result = ToolResult(
        tool=mock_tool,
        arguments={"query": "test"},
        knowledge=PDFKnowledge(retrieved_documents=[], candidates=[]),
        success=True,
    )
    mock_execute.return_value = mock_result

    # Mock final response construction
    mock_response = Response(
        answer="Mocked answer",
        source=Source.PDF,
        confidence=Confidence.HIGH,
        citations=[],
    )
    mock_build.return_value = mock_response

    mock_vector_store = MagicMock()

    res = answer_question(mock_vector_store, "Test question")

    assert res == mock_response
    mock_create.assert_called_once()
    assert mock_execute.call_count == 1
    args, _kwargs = mock_execute.call_args
    assert args[0] == mock_tool_call
    from models.tool_runtime import ToolRuntime

    assert isinstance(args[1], ToolRuntime)
    mock_build.assert_called_once()


def test_build_current_query_retains_historical_years():
    """
    Verify that _build_current_query retains specific historical years
    and only appends the current year if no year is present.
    """
    from datetime import datetime, timezone

    from services.tool_selector import _build_current_query

    current_year = str(datetime.now(timezone.utc).year)

    # 1. Query with 2011 (historical) - should NOT append current year
    q1 = "Who won Cricket world cup 2011?"
    res1 = _build_current_query(q1)
    assert "2011" in res1
    assert current_year not in res1
    assert res1 == "Who won Cricket world cup 2011?"

    # 2. Query with 1999 (historical) - should NOT append current year
    q2 = "Who won the 1999 rugby cup?"
    res2 = _build_current_query(q2)
    assert "1999" in res2
    assert current_year not in res2

    # 3. Query without year - should append current year
    q3 = "Who is the CEO of Apple?"
    res3 = _build_current_query(q3)
    assert res3.endswith(current_year)

    # 4. Query starting with a year - should NOT append current year
    q4 = "2022 CWC winner"
    res4 = _build_current_query(q4)
    assert "2022" in res4
    assert current_year not in res4
    assert res4 == "2022 CWC winner"
