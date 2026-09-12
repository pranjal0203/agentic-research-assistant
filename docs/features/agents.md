# 🤖 CrewAI Specialized Agents

This document describes the configurations, prompts, and constraints of the multi-agent cooperative crew.

---

## 👥 Agent Hierarchy & Specifications

The crew consists of three agents cooperating sequentially:

| Agent Name | Role | Backstory | Tools Allowed |
| :--- | :--- | :--- | :--- |
| **Lead Research Planner** | Plan queries and map research paths | Expert search planner. Identifies core query sequences, reads memory logs, and prevents redundant searches. | SQLite LTM match tool |
| **Evidence Specialist** | Retrieve PDF and Web information | Precision retrieval specialist. Executes search queries and compiles factual citation chunks. | PDF Search, Tavily Web Search, MCP tools |
| **Synthesis Agent** | Verify facts and compile report | Senior editor. Merges specialist logs, runs grounding checks, and outputs final Markdown text. | None (pure reasoning) |

---

## 🛡️ Bounding & Token Safety Guards

To prevent Groq context windows from overflowing and protect operations against strict rate limits, the following parameters are enforced in [`services/crew_service.py`](file:///Users/pranjalagarwal/Downloads/agentic-research-assistant/services/crew_service.py):

*   **`max_iter=3` (Max Agent Iterations):** The Specialist is restricted to at most 3 ReAct loops. This prevents loop recursion if search results are noisy.
*   **Query Count Caps:** The Planner is instructed via system prompts to draft at most 3 core search queries.
*   **Segment Size Bounds:** Content chunks returned by search tools are capped at `500` characters max, keeping the LLM context clean and cheap.

---

## 📝 Prompt Formatting Constraints

Every agent is initialized with strict instructions to preserve grounding:
1.  **Planner:** Must inspect historical context logged in LTM before planning new queries.
2.  **Specialist:** Must note document paths and webpage URLs alongside every gathered evidence point.
3.  **Synthesizer:** Must place inline file footnotes (e.g. `[Attention_is_All_You_Need.pdf]`) or URLs alongside claims, and must state limitations if the evidence is insufficient.
