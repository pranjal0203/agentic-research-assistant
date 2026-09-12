# ADR-002: Choose SQLite for Long-Term Memory (LTM) Engine

## Status
Accepted

## Context
Autonomous research crews need to remember previously compiled reports and user style preferences (concise vs. technical, comprehensive vs. quick overview). Without a persistent memory layer:
1.  Running the same topic multiple times generates duplicate Web and Chroma requests, wasting API tokens.
2.  Users have to re-enter writing style guidelines at the start of every session.
3.  The agent cannot reference historical contexts when compiling follow-up reports.

We needed a persistent, lightweight, and zero-configuration storage engine.

## Decision
We chose **SQLite** as the storage database for the Long-Term Memory (LTM) service. 
*   **Database File:** Saved locally at `db/memory.db`.
*   **Tables:** `research_history` (logs reports) and `user_preferences` (logs writing style/depth settings).

## Rationale
*   **Zero Dependency:** SQLite is built directly into Python's standard library (`sqlite3`). It requires no local server installations (unlike Redis or PostgreSQL).
*   **Persistent File Storage:** Keeps files across app restarts.
*   **Fast Querying:** Allows keyword search matching (`LIKE '%query%'`) to easily pull relevant historical context logs during planning.

## Consequences

### Positive:
*   **Token Savings:** The Planner can read past SQLite reports and skip redundant vector searches.
*   **State Persistence:** User preferences are automatically remembered across sessions.

### Negative:
*   **File Exclusion Requirement:** The database file (`db/memory.db` and any `*.db`) must be added to `.gitignore` to prevent committing local test history state into Git.
