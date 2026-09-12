from unittest.mock import MagicMock, patch

from models.confidence import Confidence
from models.response import NOT_FOUND_MESSAGE
from models.source import Source
from services.response_builder import build_response


@patch("services.response_builder.generate_answer")
@patch("services.response_builder._evaluate_confidence")
@patch("services.response_builder._determine_source")
@patch("services.response_builder.fuse_context")
@patch("services.response_builder._rank_candidates")
@patch("services.response_builder._extract_candidates")
def test_build_response_refusal_override(
    mock_extract,
    mock_rank,
    mock_fuse,
    mock_determine,
    mock_eval_conf,
    mock_gen_answer,
):
    """
    Verify that if generate_answer returns NOT_FOUND_MESSAGE,
    the metadata fields are correctly set to NONE/empty list.
    """
    mock_extract.return_value = [MagicMock()]
    mock_rank.return_value = [MagicMock()]
    mock_fuse.return_value = "Merged text context"
    mock_determine.return_value = Source.PDF
    mock_eval_conf.return_value = Confidence.HIGH
    mock_gen_answer.return_value = NOT_FOUND_MESSAGE

    res = build_response("gibberish query", (MagicMock(),))

    assert res.answer == NOT_FOUND_MESSAGE
    assert res.source == Source.NONE
    assert res.confidence == Confidence.NONE
    assert res.citations == []


@patch("services.response_builder.generate_answer")
@patch("services.response_builder._evaluate_confidence")
@patch("services.response_builder._determine_source")
@patch("services.response_builder.fuse_context")
@patch("services.response_builder._rank_candidates")
@patch("services.response_builder._extract_candidates")
def test_build_response_valid_answer(
    mock_extract,
    mock_rank,
    mock_fuse,
    mock_determine,
    mock_eval_conf,
    mock_gen_answer,
):
    """
    Verify metadata is correctly constructed for valid answers.
    """
    mock_extract.return_value = [MagicMock()]
    mock_rank.return_value = [MagicMock()]
    mock_fuse.return_value = "Merged text context"
    mock_determine.return_value = Source.PDF
    mock_eval_conf.return_value = Confidence.HIGH
    mock_gen_answer.return_value = "This is a valid answer from LLM."

    res = build_response("valid query", (MagicMock(),))

    assert res.answer == "This is a valid answer from LLM."
    assert res.source == Source.PDF
    assert res.confidence == Confidence.HIGH
