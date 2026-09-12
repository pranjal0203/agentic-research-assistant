# 🗺️ Codebase Map & Dependencies

This document provides a map of files in the repository and lists their import/dependency relationships.

---

## 📁 File Structure & Explanations

### 1. Root Files
*   [`app.py`](file:///Users/pranjalagarwal/Downloads/agentic-research-assistant/app.py) - CLI Entry point. Presents options 1-8 to the user.
*   [`requirements.txt`](file:///Users/pranjalagarwal/Downloads/agentic-research-assistant/requirements.txt) - List of application requirements (including `langchain-chroma` for CI).

### 2. Configuration (`config/`)
*   [`config/settings.py`](file:///Users/pranjalagarwal/Downloads/agentic-research-assistant/config/settings.py) - Centralized application configurations (Top-K, models, gateway, thresholds).
*   [`config/mcp_servers.json`](file:///Users/pranjalagarwal/Downloads/agentic-research-assistant/config/mcp_servers.json) - MCP stdio connection configurations.

### 3. Models Layer (`models/`)
Contains type contracts:
*   [`models/response.py`](file:///Users/pranjalagarwal/Downloads/agentic-research-assistant/models/response.py) - Struct Response contracts and refusal mapping string definitions.
*   [`models/retrieval_candidate.py`](file:///Users/pranjalagarwal/Downloads/agentic-research-assistant/models/retrieval_candidate.py) - Shared normalized retrieval candidate class.

### 4. Service Logic (`services/`)
*   [`services/crew_service.py`](file:///Users/pranjalagarwal/Downloads/agentic-research-assistant/services/crew_service.py) - Orchestrates autonomous Planner/Specialist/Synthesizer Crews.
*   [`services/memory_service.py`](file:///Users/pranjalagarwal/Downloads/agentic-research-assistant/services/memory_service.py) - Local SQLite LTM interface.
*   [`services/mcp_client.py`](file:///Users/pranjalagarwal/Downloads/agentic-research-assistant/services/mcp_client.py) - Dynamic JSON-RPC MCP connector.
*   [`services/conversation.py`](file:///Users/pranjalagarwal/Downloads/agentic-research-assistant/services/conversation.py) - Conversational RAG manager.
*   [`services/agent.py`](file:///Users/pranjalagarwal/Downloads/agentic-research-assistant/services/agent.py) - Single-agent ReAct loop executor.
*   [`services/question_rewriter.py`](file:///Users/pranjalagarwal/Downloads/agentic-research-assistant/services/question_rewriter.py) - Rewrites pronoun follow-up queries.
*   [`services/response_builder.py`](file:///Users/pranjalagarwal/Downloads/agentic-research-assistant/services/response_builder.py) - Normalizes, reranks, fuses context, and handles LLM generation.
*   [`services/reranker.py`](file:///Users/pranjalagarwal/Downloads/agentic-research-assistant/services/reranker.py) - Shared embeddings cosine similarity ranker.
*   [`services/retriever.py`](file:///Users/pranjalagarwal/Downloads/agentic-research-assistant/services/retriever.py) - Chroma vector DB search.
*   [`services/web_search.py`](file:///Users/pranjalagarwal/Downloads/agentic-research-assistant/services/web_search.py) - Tavily web search.

---

## 🔗 Dependency Map (Import Tree)

Below is the execution call tree, showing which file imports which:

```text
app.py
├── services/pipeline.py
│   └── services/index_manager.py
│       ├── models/collection.py
│       ├── services/document_discovery.py
│       ├── services/document_loader.py
│       ├── services/text_splitter.py
│       └── services/vector_store.py
├── services/conversation.py
│   ├── services/question_rewriter.py
│   │   └── services/llm.py
│   ├── services/agent.py
│   │   ├── services/tool_selector.py
│   │   ├── services/tool_executor.py
│   │   └── services/response_builder.py
│   │       ├── models/response.py
│   │       ├── services/reranker.py
│   │       │   └── services/embeddings.py
│   │       ├── services/context_fusion.py
│   │       ├── services/evaluator.py
│   │       └── services/generator.py
│   └── services/conversation_memory.py
├── services/crew_service.py
│   ├── services/memory_service.py
│   └── services/mcp_client.py
│       └── config/mcp_servers.json
└── services/memory_service.py
```
