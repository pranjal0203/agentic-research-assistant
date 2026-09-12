# 🧩 Component Overview & Interfaces

This document describes the design interfaces and class definitions for the core component layers of the application.

---

## 💾 1. Long-Term Memory (LTM) Component

The memory system interfaces with a local SQLite database (`db/memory.db`) to persist research runs and user parameters.

### Service Interface: `services/memory_service.py`

*   **`init_db() -> None`**
    Initializes tables `research_history` (id, topic, report_content, timestamp) and `user_preferences` (id, depth, style).
*   **`save_research_report(topic: str, report: str) -> None`**
    Inserts a newly generated research report text matching the topic.
*   **`get_past_context(topic: str) -> str`**
    Performs keyword matching over past logged topics to return historical reports as planning context.
*   **`get_preference() -> str`** / **`save_preference(depth: str, style: str) -> None`**
    Saves and reads depth (quick, comprehensive) and writing style guidelines.

---

## 🔌 2. Model Context Protocol (MCP) Component

Negotiates tool loading via stdio sub-processes. Employs JSON-RPC message packets to connect external server tools.

### Client Interface: `services/mcp_client.py`

*   **`class MCPClient`**
    Manages stdio subprocess pipelines. Handles initial handshakes, dynamic tool discovery, and payload wrappers:
    *   `initialize() -> dict` - Sends handshaking initialize request.
    *   `list_tools() -> list[dict]` - Retrieves server tool configurations.
    *   `call_tool(name: str, arguments: dict) -> dict` - Invokes a specific tool on the server.
*   **`load_mcp_tools(config_path: str) -> list[BaseTool]`**
    Constructs CrewAI-compatible tool classes dynamically from `config/mcp_servers.json` server specifications.

---

## 🎯 3. Retrieval, Reranking & Fusion Components

Enforces clean candidate translation, shared semantic scoring, and fact-grounding.

### Candidate Builder (`services/candidate_builder.py`)
Converts source-specific evidence inputs to normalized `RetrievalCandidate` dataclasses:
```python
@dataclass
class RetrievalCandidate:
    content: str
    source: Source      # Source.PDF, Source.WEB, Source.HYBRID
    score: float        # Unified similarity score
    citation: Citation  # Origin source title and page/url location
```

### Cosine Reranker (`services/reranker.py`)
Uses the shared embeddings model to compute cosine similarity distance vectors between the query and all candidates:
```python
def rerank_candidates(query: str, candidates: list[RetrievalCandidate]) -> list[RankedCandidate]:
    # Embeds query and candidate contents, calculates similarity scores.
```

### Context Fusion (`services/context_fusion.py`)
Groups candidates by document filename source, placing the highest-scoring chunk at the front to guarantee multi-document representation, and merges them to fit token budgets.

---

## 🤖 4. Agentic Orchestrators

### Conversational Agent (`services/agent.py`)
Executes a single-agent ReAct planning loop. Uses a dynamic `ToolRegistry` and `ToolExecutor` to plan and execute tools until evidence is gathered.

### Autonomous Crew Orchestrator (`services/crew_service.py`)
Instantiates cooperative multi-agent tasks:
```python
def run_autonomous_research(topic: str, vector_store: Chroma) -> str:
    # 1. Fetch preferences and past context from memory_service.
    # 2. Build CrewAI Agents: Planner, Specialist, Synthesizer.
    # 3. Dynamic MCP tool binding.
    # 4. Trigger crew.kickoff() and save report.
```
