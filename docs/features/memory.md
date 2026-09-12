# 💾 Long-Term Memory (LTM) Database

This guide explains the SQLite database schemas and logic used to store user preferences and historical research context.

---

## 🗄️ Database Schemas

The database file resides at `db/memory.db` and is initialized automatically by `services/memory_service.py` with the following schemas:

### 1. Table: `research_history`
Stores previously completed research runs. The Synthesizer writes to this table after a successful crew execution.
```sql
CREATE TABLE IF NOT EXISTS research_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT NOT NULL,
    report_content TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 2. Table: `user_preferences`
Stores research style guidelines, populated via Option 4 in the CLI menu.
```sql
CREATE TABLE IF NOT EXISTS user_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    depth TEXT DEFAULT 'comprehensive', -- Options: quick, comprehensive
    style TEXT DEFAULT 'technical'      -- Options: concise, technical, tutorial
);
```

---

## 🧠 Historical Context Injection Flow

Before the Lead Research Planner starts drafting queries, the crew service pulls past logs:

1.  **Retrieve Past Reports:**
    `memory_service.get_past_context(topic)` executes a database query matching topic keywords (e.g., `SELECT report_content FROM research_history WHERE topic LIKE '%BERT%'`).
2.  **Context Integration:**
    If matches exist, they are appended to the Planner's input parameters. This allows the Planner to see what was researched previously and focus on new, missing details instead of querying the web for identical facts.
3.  **Style Enforcements:**
    The user's preferred depth and writing guidelines are fed directly into the Synthesizer's system prompt instructions.
