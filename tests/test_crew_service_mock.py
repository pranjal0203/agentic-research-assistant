from unittest.mock import MagicMock, patch

from services.crew_service import run_autonomous_research


@patch("services.crew_service.Crew")
@patch("services.memory_service.save_research_report")
@patch("services.memory_service.get_past_context")
@patch("services.memory_service.get_preference")
def test_run_autonomous_research(
    mock_get_pref,
    mock_get_past,
    mock_save_report,
    mock_crew_class,
):
    """
    Verify run_autonomous_research correctly sets up the agents,
    invokes the crew kickoff, saves the report, and returns the result string.
    """
    mock_get_pref.return_value = "professional"
    mock_get_past.return_value = "Past details on topic"

    mock_crew_instance = MagicMock()
    mock_crew_instance.kickoff.return_value = "Mocked research report result."
    mock_crew_class.return_value = mock_crew_instance

    mock_vector_store = MagicMock()

    res = run_autonomous_research("Mock Topic", mock_vector_store)

    assert res == "Mocked research report result."
    mock_crew_instance.kickoff.assert_called_once()
    mock_save_report.assert_called_once_with(
        "Mock Topic",
        "Mocked research report result.",
    )
