"""
Long-Term Memory Service.

Uses SQLite to persist historical research reports, extracted facts,
and user preferences to inject into future planning tasks.
"""

import datetime
import os
import sqlite3

from config.settings import CHROMA_DB_PATH

# Use same db/ directory path
DB_DIR = CHROMA_DB_PATH.parent if hasattr(CHROMA_DB_PATH, "parent") else "db"
DB_PATH = os.path.join(DB_DIR, "memory.db")


def initialize_memory_db() -> None:
    """
    Initialize SQLite schemas if they do not exist.
    """
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Schema 1: Research History logs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS research_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT UNIQUE,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            report TEXT
        )
        """)

    # Schema 2: User preferences
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_preferences (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        """)

    # Seed default preferences if not present
    cursor.execute(
        "INSERT OR IGNORE INTO user_preferences (key, value) VALUES (?, ?)",
        ("research_depth", "comprehensive"),
    )
    cursor.execute(
        "INSERT OR IGNORE INTO user_preferences (key, value) VALUES (?, ?)",
        ("report_style", "professional technical report"),
    )

    conn.commit()
    conn.close()


def save_research_report(topic: str, report: str) -> None:
    """
    Save or update a synthesized research report.
    """
    initialize_memory_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO research_history (topic, report, timestamp)
            VALUES (?, ?, ?)
            ON CONFLICT(topic) DO UPDATE SET
                report=excluded.report,
                timestamp=excluded.timestamp
            """,
            (
                topic.strip(),
                report.strip(),
                datetime.datetime.now(datetime.timezone.utc),
            ),
        )
        conn.commit()
    finally:
        conn.close()


def get_past_context(topic: str) -> str:
    """
    Search past research history for matching keyword context.
    """
    initialize_memory_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        # Find matches by searching for common keywords
        words = [
            w.strip().lower()
            for w in topic.split()
            if len(w.strip()) > 3 and w.strip().lower() not in ("what", "with", "from")
        ]

        if not words:
            return ""

        query_clauses = " OR ".join(["topic LIKE ?" for _ in words])
        query_args = [f"%{word}%" for word in words]

        cursor.execute(
            f"SELECT topic, report FROM research_history WHERE {query_clauses} LIMIT 3",
            query_args,
        )
        rows = cursor.fetchall()

        if not rows:
            return ""

        context_blocks = []
        for past_topic, past_report in rows:
            # Extract first 600 characters as summary context
            summary = (
                past_report[:600] + "..." if len(past_report) > 600 else past_report
            )
            context_blocks.append(f"### Past Research on '{past_topic}':\n{summary}")

        return "\n\n".join(context_blocks)
    finally:
        conn.close()


def get_preference(key: str, default: str = "") -> str:
    """
    Retrieve a persisted user preference.
    """
    initialize_memory_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT value FROM user_preferences WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row[0] if row else default
    finally:
        conn.close()


def set_preference(key: str, value: str) -> None:
    """
    Persist a user preference.
    """
    initialize_memory_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO user_preferences (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value
            """,
            (key.strip(), value.strip()),
        )
        conn.commit()
    finally:
        conn.close()


def list_past_topics() -> list[tuple[str, str]]:
    """
    Return all historically researched topics with their timestamps.
    """
    initialize_memory_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT topic, timestamp FROM research_history ORDER BY timestamp DESC"
        )
        return cursor.fetchall()
    finally:
        conn.close()
