from unittest.mock import MagicMock, patch

from models.confidence import Confidence
from models.response import Response
from models.source import Source
from services.conversation import ConversationService


@patch("services.conversation.rewrite_question")
@patch("services.conversation.answer_question")
def test_conversation_ask_resolved(mock_answer, mock_rewrite):
    """
    Verify ask workflow with resolved questions.
    """
    # Mock rewrite to return resolved standalone query
    mock_rewrite_result = MagicMock()
    mock_rewrite_result.resolved = True
    mock_rewrite_result.question = "Resolved standalone query"
    mock_rewrite.return_value = mock_rewrite_result

    # Mock agent answer
    mock_response = Response(
        answer="Valid answer",
        source=Source.PDF,
        confidence=Confidence.HIGH,
        citations=[],
    )
    mock_answer.return_value = mock_response

    mock_vector_store = MagicMock()
    mock_memory = MagicMock()
    mock_memory.messages = []

    service = ConversationService(mock_vector_store, mock_memory)
    res = service.ask("What is BERT?")

    assert res == mock_response
    mock_rewrite.assert_called_once()
    mock_answer.assert_called_once_with(mock_vector_store, "Resolved standalone query")
    mock_memory.add_user_message.assert_called_once_with("What is BERT?")
    mock_memory.add_assistant_message.assert_called_once_with("Valid answer")


@patch("services.conversation.rewrite_question")
def test_conversation_ask_unresolved(mock_rewrite):
    """
    Verify ask workflow with unresolved questions.
    """
    mock_rewrite_result = MagicMock()
    mock_rewrite_result.resolved = False
    mock_rewrite.return_value = mock_rewrite_result

    mock_vector_store = MagicMock()
    mock_memory = MagicMock()

    service = ConversationService(mock_vector_store, mock_memory)
    res = service.ask("Follow up query")

    assert res is None
