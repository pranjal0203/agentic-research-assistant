from unittest.mock import MagicMock, patch

from models.citation import Citation
from models.confidence import Confidence
from models.retrieval_candidate import RetrievalCandidate
from models.source import Source
from services.evaluator import evaluate_pdf_retrieval, evaluate_web_retrieval
from services.reranker import rerank_candidates


@patch("services.reranker.embeddings")
def test_rerank_candidates(mock_embeddings):
    """
    Verify reranking computes semantic similarity scores.
    """
    mock_embeddings.embed_query.return_value = [0.1, 0.2, 0.3]
    mock_embeddings.embed_documents.return_value = [[0.1, 0.2, 0.3]]

    candidate = RetrievalCandidate(
        content="Evidence chunk about BERT.",
        source=Source.PDF,
        score=0.90,
        citation=Citation(title="BERT.pdf", location="Page 3"),
    )

    ranked = rerank_candidates("BERT query", [candidate])
    assert len(ranked) == 1
    assert ranked[0].candidate == candidate
    assert ranked[0].relevance_score > 0.0


def test_evaluator_pdf_retrieval():
    """
    Verify PDF retrieval evaluation confidence mapping.
    """
    # High similarity matches should yield high confidence
    mock_doc = MagicMock()
    mock_doc.metadata = {"score": 0.85}

    eval_result = evaluate_pdf_retrieval([(mock_doc, 0.15)])
    assert eval_result.confidence == Confidence.VERY_HIGH


def test_evaluator_web_retrieval():
    """
    Verify Web retrieval evaluation confidence mapping.
    """
    mock_result = MagicMock()
    mock_result.score = 0.90

    eval_result = evaluate_web_retrieval([mock_result])
    assert eval_result.confidence == Confidence.VERY_HIGH
