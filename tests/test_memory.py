import os
import sqlite3

import pytest

from services.memory_service import (
    DB_PATH,
    get_past_context,
    get_preference,
    initialize_memory_db,
    list_past_topics,
    save_research_report,
    set_preference,
)


@pytest.fixture(autouse=True)
def setup_clean_db():
    """
    Ensure we run with a clean test database and clean up after.
    """
    # Delete test db if exists
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
        except OSError:
            pass

    initialize_memory_db()
    yield

    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
        except OSError:
            pass


def test_db_initialization():
    """
    Verify tables are created.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()

    assert "research_history" in tables
    assert "user_preferences" in tables


def test_save_and_retrieve_report():
    """
    Verify we can save reports and list them.
    """
    topic = "Test Topic on Quantum Computing"
    report = "This is a detailed synthesized report content."

    save_research_report(topic, report)

    past = list_past_topics()
    assert len(past) == 1
    assert past[0][0] == topic

    # Test update conflict resolution
    updated_report = "This is updated report content."
    save_research_report(topic, updated_report)
    past = list_past_topics()
    assert len(past) == 1

    # Verify context extraction
    context = get_past_context("Quantum Computing details")
    assert "Test Topic on Quantum Computing" in context
    assert "updated report" in context


def test_user_preferences():
    """
    Verify setting and retrieving preferences.
    """
    assert get_preference("research_depth") == "comprehensive"  # Seeded default
    set_preference("research_depth", "quick overview")
    assert get_preference("research_depth") == "quick overview"

    set_preference("custom_key", "custom_value")
    assert get_preference("custom_key") == "custom_value"
    assert get_preference("non_existent", "default_val") == "default_val"
