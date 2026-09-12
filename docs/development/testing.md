# 🧪 Testing & Code Coverage

This guide describes how to run tests, configure coverage metrics, and understand the test mocks.

---

## 📦 Running Tests

The test suite is built on **pytest** and is located inside the `tests/` directory.

### Run Unit Tests
To run all unit tests locally:
```bash
pytest -v
```

### Run Coverage Reports
We use `pytest-cov` to measure statement coverage. To run coverage and check code percentage:
```bash
pytest --cov=services --cov=models tests/
```
Currently, active test coverage stands at **52%**.

---

## 🔌 Bypassing External Network Calls
By default, tests that call external LLM providers (Groq) or search engines (Tavily) are **skipped** during local test runs. This keeps the test suite fast and independent of API keys.

To explicitly execute integration tests with live network calls:
```bash
RUN_LLM_TESTS=true RUN_TAVILY_TESTS=true pytest -v
```

---

## 🛠️ Mock Architecture Overview
To run tests in CI pipelines where API keys are absent, we employ `unittest.mock` inside our test files:

### 1. Global Dummies (`tests/conftest.py`)
Intercepts the test collection phase and declares default dummy variables:
```python
import os
os.environ["TAVILY_API_KEY"] = "dummy_tavily_api_key"
os.environ["GROQ_API_KEY"] = "dummy_groq_api_key"
```

### 2. Crew Mocks (`tests/test_crew_service_mock.py`)
Mocks the `Crew` class kickoff outcome to verify that data variables parse, SQLite databases record history, and reports export correctly without calling Groq:
```python
@patch("services.crew_service.Crew")
@patch("services.memory_service.save_research_report")
def test_run_autonomous_research(mock_save, mock_crew):
    mock_crew_instance = MagicMock()
    mock_crew_instance.kickoff.return_value = "Mocked research report result."
    mock_crew.return_value = mock_crew_instance
```
