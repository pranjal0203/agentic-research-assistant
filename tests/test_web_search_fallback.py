from unittest.mock import patch

from models.web_result import WebResult


@patch("services.web_search.client")
def test_search_web_valid_results(mock_client):
    """
    Verify search results parsing and mapping.
    """
    mock_client.search.return_value = {
        "results": [
            {
                "title": "BERT paper",
                "url": "http://bert-url",
                "content": "BERT stands for bidirectional encoder...",
                "score": 0.95,
            }
        ]
    }

    # Import locally because import-time environment check executes
    from services.web_search import search_web

    results = search_web("BERT paper details")
    assert len(results) == 1
    assert isinstance(results[0], WebResult)
    assert results[0].title == "BERT paper"
    assert results[0].content.startswith("BERT stands")
    assert results[0].score == 0.95
