# 📖 Intelligent Agentic Research Assistant -- Codebase Flow & Architecture Guide

This document provides a comprehensive guide to the codebase, tracing the detailed flow of execution for each mode of operation and mapping the responsibilities of each file.

---

## 🗺️ Architectural Flow Overviews

The application operates in two distinct modes: **Conversational Interactive RAG Mode** (Option 1) and **Autonomous Multi-Agent Crew Mode** (Option 2).

### Flow A: Conversational Interactive RAG (Option 1)

When you ask a question in the interactive Q&A session, the query goes through the following sequence:

```
[User Query]
    │
    ▼
1. CLI (app.py) ──► Passes query to ConversationService.ask()
    │
    ▼
2. Conversation Context Resolution (services/conversation.py)
    ├── Reads memory window history from ConversationMemory.
    └── Calls QuestionRewriter (services/question_rewriter.py) to resolve pronouns.
         ├── If missing pronouns/references: Asks user for clarification.
         └── If standalone query: Proceeds to step 3.
    │
    ▼
3. Agent Execution Loop (services/agent.py)
    ├── ToolSelector fetches available tools from ToolRegistry.
    ├── Agent plans which tools (PDF/Web) are required to retrieve evidence.
    ├── ToolExecutor runs selected tools:
    │    ├── PDFTool retrieves vector segments from services/retriever.py (Chroma DB).
    │    └── WebTool retrieves web URLs from services/web_search.py (Tavily).
    └── Loop repeats for follow-up questions up to MAX_AGENT_ITERATIONS.
    │
    ▼
4. Response Assembly & Refinement (services/response_builder.py)
    ├── Normalizes outputs into RetrievalCandidate models.
    ├── Semantically sorts candidates via embeddings similarity (services/reranker.py).
    ├── Merges candidate texts into structured text via Context Fusion (services/context_fusion.py).
    ├── Calculates confidence score (services/evaluator.py).
    └── Refusal Fallback Guard: If generator (services/generator.py) returns NOT_FOUND_MESSAGE,
        overrides source/confidence to NONE and clears citations.
```

---

### Flow B: Autonomous Multi-Agent Research Crew (Option 2)

When you trigger a deep research topic, the workflow runs completely asynchronously through a cooperative agent crew:

```
[Research Topic]
    │
    ▼
1. CLI (app.py) ──► Triggers run_autonomous_research() (services/crew_service.py)
    │
    ▼
2. Long-Term Memory Lookup (services/memory_service.py)
    ├── Queries SQLite (db/memory.db) for historical research logs matching the topic.
    └── Fetches custom user style (concise/tutorial) and depth preferences.
    │
    ▼
3. Model Context Protocol Connection (services/mcp_client.py)
    ├── Handshakes with connected servers defined in config/mcp_servers.json.
    └── Dynamically translates server functions into CrewAI-compatible tools.
    │
    ▼
4. CrewAI Kickoff (services/crew_service.py)
    ├── Planner Agent: Drafts a query search plan.
    ├── Evidence Specialist: Runs retrieval tools (vector database & web search) within TPM limits.
    └── Synthesizer Agent: Compiles findings, verifies facts, and exports markdown report.
    │
    ▼
5. Output Export & Database Logging
    ├── Writes complete Markdown report file to outputs/research_report_<timestamp>.md.
    └── Logs the research run and final text to the SQLite database.
```

---

## 🗃️ Module-by-Module Code Map

### 1. `models/` (Data Contracts)
These models define immutable schemas and structured dataclasses to enforce strong typing throughout the workspace:

*   [`models/response.py`](file:///Users/pranjalagarwal/Downloads/agentic-research-assistant/models/response.py): Defines the final `Response` payload containing `answer`, `source`, `confidence`, and `citations`. Houses the public `NOT_FOUND_MESSAGE` fallback refusal constant.
*   [`models/collection.py`](file:///Users/pranjalagarwal/Downloads/agentic-research-assistant/models/collection.py): Stores document collection properties (`name`, `path`, `documents`).
*   [`models/retrieval_candidate.py`](file:///Users/pranjalagarwal/Downloads/agentic-research-assistant/models/retrieval_candidate.py): Standardizes evidence segments across both PDF distance matrices and web search relevance outputs.
*   [`models/tool_call.py`](file:///Users/pranjalagarwal/Downloads/agentic-research-assistant/models/tool_call.py) / [`models/tool_result.py`](file:///Users/pranjalagarwal/Downloads/agentic-research-assistant/models/tool_result.py): Manages agent tool invocation state.

---

### 2. `services/` (Business Logic & Pipelines)

#### Core Multi-Agent & Memory Layer:
*   [`services/crew_service.py`](file:///Users/pranjalagarwal/Downloads/agentic-research-assistant/services/crew_service.py): Orchestrates CrewAI agents. Defines specific constraints (`max_iter`, output character limits) to safeguard operations against rate limits.
*   [`services/memory_service.py`](file:///Users/pranjalagarwal/Downloads/agentic-research-assistant/services/memory_service.py): Manages SQLite memory initialization (`db/memory.db`) and SQL queries for logging reports and editing preferences.
*   [`services/mcp_client.py`](file:///Users/pranjalagarwal/Downloads/agentic-research-assistant/services/mcp_client.py): Spawns JSON-RPC stdio subprocesses to negotiate dynamic tool bindings.

#### RAG & Retrieval Layer:
*   [`services/conversation.py`](file:///Users/pranjalagarwal/Downloads/agentic-research-assistant/services/conversation.py): Coordinates the RAG question routing and message memory.
*   [`services/question_rewriter.py`](file:///Users/pranjalagarwal/Downloads/agentic-research-assistant/services/question_rewriter.py): Uses the LLM to rewrite contextual queries into standalone search questions.
*   [`services/agent.py`](file:///Users/pranjalagarwal/Downloads/agentic-research-assistant/services/agent.py): Drives the single-agent ReAct planning loop.
*   [`services/retriever.py`](file:///Users/pranjalagarwal/Downloads/agentic-research-assistant/services/retriever.py): Performs similarity searches inside local Chroma DB.
*   [`services/web_search.py`](file:///Users/pranjalagarwal/Downloads/agentic-research-assistant/services/web_search.py): Queries the Tavily Search API with advanced options.
*   **Ranking & Evaluation:**
    *   [`services/reranker.py`](file:///Users/pranjalagarwal/Downloads/agentic-research-assistant/services/reranker.py): Leverages Hugging Face embeddings to compute similarity cosine distances for cross-source sorting.
    *   [`services/evaluator.py`](file:///Users/pranjalagarwal/Downloads/agentic-research-assistant/services/evaluator.py): Scores candidate relevance to assign Confidence values.

---

### 3. `config/` (Parameters)
*   [`config/settings.py`](file:///Users/pranjalagarwal/Downloads/agentic-research-assistant/config/settings.py): Centralizes all configurations, including document chunk sizes, relevance thresholds, models, and AI gateway settings.

---

## 🔧 Core Mechanics Trace: PDF vs Web Retrieval

The retrieval adapter maps source-specific evidence classes to standard candidates:

```
PDF Document chunk ──► LangChain Document ──► RetrievalCandidate(
                                                 content=doc.page_content,
                                                 source=Source.PDF,
                                                 score=score,
                                                 citation=Citation(
                                                    title=doc.metadata["source"],
                                                    location=doc.metadata["page"]
                                                 )
                                              )

Tavily Result ────────► WebResult ──────────► RetrievalCandidate(
                                                 content=result.content,
                                                 source=Source.WEB,
                                                 score=result.score,
                                                 citation=Citation(
                                                    title=result.title,
                                                    location=result.url
                                                 )
                                              )
```
This candidate normalization ensures that the reranker can compute shared semantic cosine similarity distances across both sources concurrently.
