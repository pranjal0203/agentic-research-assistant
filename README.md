# 🤖 Agentic Research Assistant

> **Building a production-quality AI Research Assistant---one release at
> a time.**

A production-oriented AI application built with **Python, LangChain, CrewAI, ChromaDB, Hugging Face, Groq, and Tavily**, following modern software
engineering principles while progressively evolving from a
Retrieval-Augmented Generation (RAG) system into a fully autonomous
**Agentic AI Research Assistant**.

Rather than focusing solely on implementing AI features, this project
emphasizes **clean architecture, modular design, maintainability, and
scalable software engineering practices**. Each release introduces
meaningful capabilities while preserving a well-structured codebase that
can evolve into a production-ready intelligent assistant.

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![LangChain](https://img.shields.io/badge/LangChain-LCEL-green)
![CrewAI](https://img.shields.io/badge/Crew-CrewAI-cyan)
![ChromaDB](https://img.shields.io/badge/Vector%20Database-Chroma-orange)
![Groq](https://img.shields.io/badge/LLM-Groq-red)
![Tavily](https://img.shields.io/badge/Search-Tavily-purple)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Active-success)

------------------------------------------------------------------------

# 🌟 Vision

Large Language Models become truly valuable when they can **retrieve
reliable information, reason over it, evaluate the quality of retrieved
knowledge, and interact with external tools**.

This repository documents that journey.

Instead of building a simple "Chat with PDF" application, this project
incrementally develops a production-oriented AI research assistant while
applying modern software engineering principles, clean architecture, and
modular design.

Each release focuses on introducing meaningful capabilities without
sacrificing maintainability or code quality. The long-term goal is to
evolve this project into a fully autonomous **Agentic AI Research
Assistant** capable of planning, reasoning, retrieving information from
multiple knowledge sources, and orchestrating external tools.

------------------------------------------------------------------------

# 🚀 Current Capabilities

The current implementation provides:

-   📄 Retrieval-Augmented Generation (RAG) over PDF documents
-   🌐 AI-powered web search using Tavily
-   🔀 Adaptive PDF-only, Hybrid, and Web-only retrieval strategies
-   🤖 **Autonomous Multi-Agent Crew (v3.0.0):** Specialized Lead Research Planner, Evidence Specialist, and Synthesis Agent cooperating for deep research.
-   💾 **Long-Term Memory (LTM) database (v3.0.0):** SQLite engine mapping past contexts and custom style preferences.
-   🔌 **Model Context Protocol (v3.0.0):** stdio client dynamically mapping server tools into the researcher agent's loop.
-   🔗 True hybrid retrieval across PDF and Web evidence
-   🧩 Normalized cross-source retrieval candidates
-   🎯 Embedding-based cross-source reranking
-   🏆 Ranked evidence selection with configurable Hybrid Top-K
-   🧬 Structured multi-source context fusion
-   🔍 Semantic retrieval using ChromaDB
-   🧠 Hugging Face Sentence Transformer embeddings
-   ⚡ Groq LLM integration
-   📊 Confidence-based retrieval evaluation
-   📑 PDF, Web, and Hybrid source attribution with citations
-   🧩 Structured response models
-   🔧 Dynamic tool registry and execution adapters
-   🔄 Bounded multi-step agent loop with observations
-   🛡️ Duplicate-call and per-tool execution safeguards
-   🏗️ Clean layered architecture
-   ⚙️ Centralized configuration management
-   🔐 Centralized environment initialization
-   📦 Persistent vector database
-   📚 Multiple document collections
-   🗂️ Dynamic collection discovery
-   ♻️ Automatic document index rebuilding
-   📄 Generic document loading pipeline
-   📑 Manifest-based index synchronization
-   📝 Fully typed and documented codebase
-   💬 Context-aware multi-turn conversations
-   🧠 Bounded in-session conversation memory
-   ✍️ Standalone question rewriting for follow-up retrieval
-   🔗 Pronoun and conversational reference resolution
-   🛡️ Unresolved-context detection before retrieval
-   🧹 Conversation memory reset with the `clear` command
-   🧪 Extensive unit test coverage (52% code coverage) under mocked environments
-   🔄 Extensible architecture for future AI capabilities

------------------------------------------------------------------------

# 🎯 Current Release

## **v3.0.0 -- Autonomous Multi-Agent Crews & Long-Term Memory (LTM) Architecture**

### ✨ Highlights

-   🤖 **Multi-Agent CrewAI Orchestration:** Replaced the single-agent pipeline with a cooperative Crew of three specialized agents:
    *   **Lead Research Planner:** Analyzes the topic, queries past contexts, and drafts a structured search query plan.
    *   **Evidence Retrieval Specialist:** Executes search tools (local database and web) to collect facts.
    *   **Synthesis & Verification Specialist:** Compiles findings, runs grounding checks, and builds the final Markdown report.
-   💾 **SQLite Long-Term Memory (LTM) Engine:** Created a persistent SQLite database (`db/memory.db`) storing:
    *   `research_history`: Logs past topics and generated reports.
    *   `user_preferences`: Stores user depth (comprehensive vs. quick overview) and style guidelines (technical, concise, tutorial).
-   🔌 **Model Context Protocol (MCP) Client:** Implemented stdio-based JSON-RPC transport client connecting to local MCP servers. Dynamically discovers tools and exposes them to the researcher crew.
-   🛡️ **Rate-Limit & Token Safeguards:** Constrained agent ReAct iterations (`max_iter=3`), query counts (max 3), and tool observation chunks (capped to `500` characters) to strictly fit inside Groq's 8,000 TPM limit.
-   ⚖️ **Metadata Refinement:** Configured fallback overrides setting `Source.NONE`, `Confidence.NONE`, and empty citations when the generator issues an unknown refusal message (*"I don't have enough information..."*).

---

# 📜 Previous Releases

## **v2.9.6 -- OmniRoute AI Gateway Integration**

### ✨ Highlights

-   🌐 **OmniRoute AI Gateway Integration:** Configured standard OpenAI-compatible client routing through a local proxy to support auto-fallback across multiple API keys, round-robin load balancing, and prompt token compression.
-   🧪 **Clean Proxy Call Path:** Swapped from `ChatGroq` to `ChatOpenAI` when using the gateway, resolving the `404 Unknown API Route` bug caused by the Groq SDK client library appending custom namespaces.
-   🛠️ **Configurable Toggle:** Added the `USE_OMNIROUTE` toggle and `OMNIROUTE_API_BASE` parameters to `config/settings.py` for backward-compatible routing.
-   📂 **Key Validation Bypass:** Configured an automatic dummy key fallback so local testing scripts do not get blocked if the developer's shell environment is missing API credentials.
-   📝 **Diagnostic Verification Script:** Added a test harness `scratch/test_omniroute.py` to easily check proxy connections, query routing, and key health.

### What's New in v2.9.6?

v2.9.6 introduces integration support for **OmniRoute AI Gateway** (built by `diegosouzapw/OmniRoute`), a self-hosted AI proxy that acts as a unified OpenAI-compatible endpoint.

By toggling `USE_OMNIROUTE = True` in configurations, all LLM client calls are automatically routed to the local OmniRoute instance (running by default at `http://localhost:20128/v1`). To support this cleanly, we transitioned the client factory to use `ChatOpenAI`, preventing the Groq Python SDK from appending redundant namespaces that previously caused `404` routing exceptions. 

This enables developers and testing tools to round-robin requests across multiple API credentials (such as multiple free Groq keys and OpenRouter fallback accounts). When a primary key hits a rate limit, the proxy catches the `429` error in the background and seamlessly retries the request using the next available key in the priority chain. This ensures our multi-turn, multi-step scenario test suite can execute completely uninterrupted and at full speed.

---

## **v2.9.5 -- Optimization and Comparative RAG**

### ✨ Highlights

-   🏆 **Prioritized Document-Level Source Diversity:** Grouped candidate sources by their exact document filename and placed the top representative of each document at the front of the candidate list. This guarantees multi-document representation in the generator context and prevents diverse papers from being discarded.
-   🎯 **Optimized Relevance Thresholds:** Tuned `MIN_SOURCE_RELEVANCE = 0.40` to allow secondary documents in comparative queries to pass representation filters without being blocked by lexical match drag.
-   🔗 **Comparative Pronoun Resolution:** Added comparative and relative reference words (`one`, `ones`, `former`, `latter`) to the question rewriter's fast-path pronoun detector to successfully resolve follow-up comparison queries.
-   ⚡ **Token Budget Tuning & Prompt Compression:** Compressed planning and generator prompt templates to save ~1,500 instruction tokens per agent loop, and raised chunk size to `1200` to capture richer semantic contexts.
-   📂 **Collection-Aware Agent Routing:** Exposed selected folder names and document lists to agent planners, allowing the LLM to bypass document searches for external topics and prevent web search pollution for local topics.
-   🧪 **Robust Workspace Integration:** Added Pyright virtual environment settings (`pyrightconfig.json`) and pytest exclusions (`pytest.ini`) to eliminate workspace import warnings.
-   🧹 **Codebase Housekeeping & Refactoring:** Deleted 6 legacy, obsolete files (saving 396 lines of dead code) to streamline the directory structure, and moved hardcoded evaluator confidence thresholds into centralized settings.

### What's New in v2.9.5?

v2.9.5 introduces key optimizations, bug fixes, and calibration updates to stabilize the agent before v3 development.

A major enhancement is the **Document-Level Source Diversity** logic in the cross-source reranker. Previously, the reranker grouped candidates by general source type (PDF vs. Web) and sorted all items strictly by raw relevance score before slicing. This caused secondary documents (which typically have slightly lower lexical similarity for multi-concept queries) to be pushed below the top-k threshold and discarded. We now group candidates by individual document filename and place their top representatives at the front of the list, ensuring true multi-document grounding and citations for comparative questions.

Additionally, the **Question Rewriter**'s pronoun resolution was expanded to detect relative and comparative reference words. This resolves follow-up queries like *"Which one is larger?"* or *"Compare the former with the latter"* by referencing the conversation history.

Finally, prompts were compressed and token budgets were tuned, the agent planner was made **Collection-Aware** to prevent redundant tool executions, and all legacy pre-agent RAG files and static routers were deleted to clean up the codebase. Hardcoded evaluation confidence ranges were also extracted into centralized settings to keep the code fully configuration-driven.

---

## **v2.9.0 -- Intelligent Agentic Retrieval**

### ✨ Highlights

-   🤖 LLM-powered tool selection from a dynamic tool registry
-   🧩 Registry-driven tool capabilities and metadata
-   🔧 Generic tool-call validation before execution
-   🔄 ReAct-style planner → tool → observation → follow-up loop
-   🧠 Multi-step retrieval with bounded agent iterations
-   🛡️ Per-tool execution limits and duplicate-call prevention
-   🌐 Improved current-information Web query construction
-   🔎 Deeper Tavily Web retrieval using advanced search
-   🔀 Generic PDF, Web, and Hybrid evidence orchestration
-   🎯 Cross-source semantic reranking with shared embeddings
-   🏆 Source-aware Hybrid Top-K evidence selection
-   🧬 Structured context fusion with citation preservation
-   🛡️ Grounded answer generation that refuses unsupported claims
-   💬 Context-aware multi-turn conversations
-   ✍️ Standalone follow-up question rewriting
-   🔗 Pronoun and conversational reference resolution
-   🧹 `clear` command for resetting session memory
-   🏗️ Modular agent, tool registry, runtime, and execution layers
-   🔄 Architecture designed to support additional tools without changing
    core agent orchestration

### What's New in v2.9.0?

v2.9.0 completes the transition from a fixed retrieval workflow into a
registry-driven agentic retrieval architecture.

The agent now receives a catalog of registered tools and asks the language
model to select the minimum set of tools required for the user's question.
Selected calls are validated against the registry before execution, so the
agent does not need PDF- or Web-specific routing logic.

After execution, tool observations are fed back into the planner. When the
initial retrieval does not provide usable evidence, the planner may request
a bounded follow-up retrieval step. Duplicate calls and per-tool execution
limits prevent unnecessary repeated work.

Web retrieval was also improved for current-information questions. The
planner constructs more explicit, time-aware queries when appropriate,
while the Web search service remains generic and simply executes the query
through Tavily. This keeps search behavior extensible without embedding
domain-specific rules into the Web service.

The final answer remains strictly grounded in retrieved evidence. If the
available evidence cannot establish an important part of the question, the
generator explicitly reports the limitation rather than filling the gap
with unsupported model knowledge.

# 🏛️ System Architecture

``` text
                               User Question
                                    │
                                    ▼
                                   app.py
                                    │
                                    ▼
                          ConversationService
                          ┌─────────┴─────────┐
                          │                   │
                          ▼                   ▼
                  ConversationMemory   Question Rewriter
                          │                   │
                          │             RewriteResult
                          │                   │
                          └─────────┬─────────┘
                                    │
                              resolved?
                         ┌──────────┴──────────┐
                         │                     │
                         ▼                     ▼
                    unresolved              resolved
                         │                     │
                         ▼                     ▼
                  Ask user to clarify    Agent Orchestrator
                                               │
                                               ▼
                                        Tool Selector
                                               │
                                               ▼
                                        Tool Registry
                                               │
                         ┌─────────────────────┼─────────────────────┐
                         ▼                     ▼                     ▼
                    PDF Tool              Web Tool             Future Tools
                         │                     │                     │
                         └─────────────────────┼─────────────────────┘
                                               ▼
                                        Tool Executor
                                               │
                                               ▼
                                          Observation
                                               │
                                               ▼
                                      Follow-up Planner
                                               │
                                  ┌────────────┴────────────┐
                                  │                         │
                                  ▼                         ▼
                              More tools                 Stop
                                  │                         │
                                  └────────────┬────────────┘
                                               ▼
                                      Retrieval Candidates
                                               │
                                               ▼
                                   Cross-Source Reranker
                                               │
                                               ▼
                                         HYBRID_TOP_K
                                               │
                                               ▼
                                        Context Fusion
                                       ┌────────┴────────┐
                                       ▼                 ▼
                                    Context           Citations
                                       │
                                       ▼
                                 Grounded Generator
                                       │
                                       ▼
                                   LLM Client
                                       │
                                       ▼
                                    Response
                         (Answer • Source • Confidence • Citations)
                                       │
                                       ▼
                              Update ConversationMemory
```

The application separates conversational orchestration, agent planning,
tool execution, retrieval, evidence ranking, and answer generation.

-   **Conversation Service** coordinates context resolution and memory
    updates.
-   **Conversation Memory** stores a bounded in-session history of typed
    user and assistant messages.
-   **Question Rewriter** converts contextual follow-ups into standalone
    retrieval questions and identifies missing conversational context.
-   **Agent Orchestrator** coordinates planning, tool execution,
    observations, and bounded follow-up planning.
-   **Tool Selector** builds its planning catalog dynamically from the
    registered tools instead of hardcoding PDF or Web routing.
-   **Tool Registry** describes available tools, their arguments, scope,
    selection guidance, and current-information requirements.
-   **Tool Executor** maps registered tools to their implementation
    adapters.
-   **PDF Tool** retrieves local evidence from the selected Chroma
    collection.
-   **Web Tool** retrieves external evidence through the generic Tavily
    search service.
-   **Candidate Builder** converts source-specific results into a common
    `RetrievalCandidate` representation.
-   **Reranker** compares PDF and Web candidates in one embedding space.
-   **Context Fusion** combines the strongest ranked evidence while
    preserving citations.
-   **Generator** produces a grounded answer from the fused context.
-   **Response models** provide a consistent answer, source, confidence,
    and citation interface.

The agent is intentionally registry-driven. Adding a new retrieval tool
should primarily require registering its metadata and executor rather than
changing the core agent orchestration.

PDF distance and Tavily relevance values are never directly compared
because they have different score semantics.

# 📁 Project Structure

``` text
intelligent-agentic-research-assistant/
│
├── app.py                      # Interactive CLI application entry point
├── config/
│   ├── settings.py             # Centralized application parameters
│   └── mcp_servers.json        # MCP server connection configurations
├── data/                       # Local document collection directories
├── db/                         # Chroma DB vector database files (ignored)
├── scratch/                    # Temporary and diagnostic test scripts
├── models/                     # Type contracts and dataclasses
│   ├── agent_state.py
│   ├── citation.py
│   ├── collection.py
│   ├── confidence.py
│   ├── context.py
│   ├── conversation_message.py
│   ├── knowledge.py
│   ├── ranked_candidate.py
│   ├── response.py
│   ├── retrieval_candidate.py
│   ├── retrieval_evaluation.py
│   ├── rewrite_result.py
│   ├── source.py
│   ├── tool.py
│   ├── tool_call.py
│   ├── tool_result.py
│   ├── tool_runtime.py
│   └── web_result.py
├── services/
│   ├── __init__.py
│   ├── agent.py
│   ├── agent_planner.py
│   ├── candidate_builder.py
│   ├── context_fusion.py
│   ├── conversation.py
│   ├── conversation_memory.py
│   ├── crew_service.py         # CrewAI agent setup and kickoff
│   ├── memory_service.py       # SQLite database queries and preferences
│   ├── mcp_client.py           # stdio JSON-RPC MCP tool wrappers
│   ├── document_discovery.py
│   ├── document_loader.py
│   ├── embeddings.py
│   ├── evaluator.py
│   ├── generator.py
│   ├── index_manager.py
│   ├── knowledge/
│   │   ├── pdf.py
│   │   └── web.py
│   ├── llm.py
│   ├── pipeline.py
│   ├── question_rewriter.py
│   ├── reranker.py
│   ├── response_builder.py
│   ├── retriever.py
│   ├── text_splitter.py
│   ├── tool_executor.py
│   ├── tool_registry.py
│   ├── tool_selector.py
│   ├── tools/
│   │   ├── pdf_tool.py
│   │   └── web_tool.py
│   ├── vector_store.py
│   └── web_search.py
├── tests/
│   ├── conftest.py             # Global dummy environments setups
│   ├── test_agent_workflow.py  # Mocked ReAct agent assertions
│   ├── test_conversation_memory.py
│   ├── test_conversation_service.py
│   ├── test_crew_service_mock.py
│   ├── test_mcp.py
│   ├── test_memory.py
│   ├── test_pipeline_services.py
│   ├── test_reranker_evaluator.py
│   ├── test_response_builder.py
│   ├── test_rewriter.py
│   ├── test_tavily.py
│   └── test_web_search_fallback.py
├── requirements.txt
├── README.md
├── LICENSE
└── .env
```

### Directory Overview

| Directory | Purpose |
| :--- | :--- |
| `config/` | Centralized application configuration |
| `models/` | Typed domain models, including agent and tool contracts |
| `services/` | Business logic and application services |
| `services/knowledge/` | Source-specific knowledge retrieval abstractions |
| `services/tools/` | Registered tool execution adapters |
| `db/` | Persistent Chroma vector databases (one per collection) |
| `data/` | Collection-based local knowledge base |
| `tests/` | Deterministic unit tests and opt-in external integration tests |

# ⚙️ Technology Stack

| Technology | Purpose |
| :--- | :--- |
| **Python 3.12** | Core programming language |
| **LangChain** | LLM application framework |
| **CrewAI** | Multi-Agent Orchestrator |
| **ChromaDB** | Persistent vector database |
| **Hugging Face** | Sentence Transformer embeddings |
| **Groq** | Large Language Model inference |
| **Tavily** | AI-powered web search |
| **SQLite** | Long-Term Memory (LTM) database engine |
| **PyPDF** | PDF document processing |
| **python-dotenv** | Environment variable management |
| **langchain-openai** | OpenAI-compatible client integrations |
| **OmniRoute (Optional)** | Self-hosted local AI proxy gateway |

------------------------------------------------------------------------

# 🏗️ Software Design Principles

The project is designed around modern software engineering practices
rather than simply implementing AI functionality.

Some of the architectural principles used include:

-   Single Responsibility Principle (SRP)
-   Separation of Concerns
-   Domain-driven models
-   Null Object Pattern
-   Service-oriented architecture
-   Strong typing throughout the codebase
-   Immutable response objects
-   Modular and extensible design

The goal is to create a codebase that remains maintainable as additional
capabilities such as conversation memory, multi-document knowledge
bases, and AI agents are introduced.

------------------------------------------------------------------------

# 🚀 Getting Started

Follow these steps to set up and run the Intelligent Agentic Research
Assistant locally.

## 1. Clone the Repository

``` bash
git clone https://github.com/pranjal0203/agentic-research-assistant.git

cd intelligent-agentic-research-assistant
```

------------------------------------------------------------------------

## 2. Create a Virtual Environment

### macOS / Linux

``` bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows

``` powershell
python -m venv .venv
.venv\Scripts\activate
```

------------------------------------------------------------------------

## 3. Install Dependencies

``` bash
pip install -r requirements.txt
```

------------------------------------------------------------------------

## 4. Configure Environment Variables

Create a `.env` file in the project root.

``` env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
```

------------------------------------------------------------------------

## 5. Configure the Application

Most application settings can be customized from:

``` text
config/settings.py
```

This includes:

-   PDF document path
-   Embedding model
-   Chroma database location
-   Chunk size
-   Chunk overlap
-   Retrieval Top-K
-   Hybrid reranking Top-K (`HYBRID_TOP_K`)
-   PDF retrieval threshold
-   Web retrieval threshold
-   Tavily search configuration
-   LLM model
-   Temperature
-   Conversation memory limit (`MAX_CONVERSATION_MESSAGES`)

------------------------------------------------------------------------

## 6. Build the Vector Database

The first time you run the application, the PDF is indexed into the
persistent Chroma vector database.

Subsequent executions reuse the existing database automatically.

## 7. Run the Assistant

``` bash
python app.py
```

During a session:

-   Type `exit` to quit.
-   Type `clear` to reset conversation memory without restarting the
    application.

------------------------------------------------------------------------

## 8. Run via AI Gateway (OmniRoute) [Optional]

To bypass rate limits during testing and enable auto-fallback across multiple API keys:

1. **Spin up local OmniRoute instance** via Docker:
   ```bash
   docker run -d -p 20128:20128 -v omniroute-data:/app/data diegosouzapw/omniroute:latest
   ```
2. Navigate to the dashboard at `http://localhost:20128` (default login is `admin` / `CHANGEME`) and register your credentials under "Providers".
3. Open [`config/settings.py`](file:///Users/pranjalagarwal/Downloads/agentic-research-assistant/config/settings.py) and change the toggle setting:
   ```python
   USE_OMNIROUTE: bool = True
   ```
4. Test the proxy connectivity:
   ```bash
   PYTHONUNBUFFERED=1 PYTHONPATH=. ./venv/bin/python scratch/test_omniroute.py
   ```

------------------------------------------------------------------------

# 💬 Example Session

``` text
🤖 Intelligent Agentic Research Assistant
Type 'exit' to quit.
Type 'clear' to clear conversation memory.

You: What is self-attention?

Self-attention is an attention mechanism that relates different positions
of a sequence in order to compute a representation of that sequence.

Source: PDF
Confidence: High

You: Why is it useful?

Self-attention is useful because it can directly model relationships
between positions in the sequence and supports parallel computation.

Source: PDF
Confidence: High

You: Who is the CEO of OpenAI?

Sam Altman is the CEO of OpenAI.

Source: Web
Confidence: Very High

You: What company does he lead?

Sam Altman is the CEO of OpenAI.

Source: Web
Confidence: High

You: clear

🧹 Conversation memory cleared.

You: What company does he lead?

I need more context to understand your question. Please clarify what
you are referring to.
```

The follow-up question is rewritten internally for retrieval while the
original user message is retained in conversation memory. After `clear`,
the missing reference is detected before retrieval.

------------------------------------------------------------------------

# 🔌 Model Context Protocol (MCP) Setup

To connect filesystem tools or custom APIs:
1. Open [`config/mcp_servers.json`](file:///Users/pranjalagarwal/Downloads/agentic-research-assistant/config/mcp_servers.json).
2. Configure your server command and arguments:
   ```json
   {
     "mcpServers": {
       "filesystem": {
         "command": "node",
         "args": ["/path/to/server/index.js", "/path/to/data"]
       }
     }
   }
   ```
3. During autonomous research (Option 2), the system will connect to the server, discover tools, and provide them to the researcher agent automatically.

------------------------------------------------------------------------

# ⚙️ Configuration

Application behavior is centralized in:

``` text
config/settings.py
```

### Retrieval

-   Number of PDF chunks retrieved
-   PDF retrieval threshold
-   Web retrieval threshold
-   Hybrid reranking Top-K (`HYBRID_TOP_K`)
-   Chunk size
-   Chunk overlap

### Embeddings

-   Hugging Face embedding model
-   Embedding cache
-   Shared embedding space for cross-source reranking

### LLM

-   Groq model
-   Temperature

### AI Gateway (OmniRoute)

-   `USE_OMNIROUTE`: Enable/disable routing requests through the local OmniRoute proxy gateway.
-   `OMNIROUTE_API_BASE`: Mapped default local proxy URL (`http://localhost:20128/v1`).

### Web Search

-   Tavily search depth
-   Maximum search results
-   Generic execution of planner-generated search queries
-   Current-information query construction in the agent planner

### Conversation Memory

-   Maximum retained conversation messages (`MAX_CONVERSATION_MESSAGES`)
-   The limit must be positive and even so normal history windows
    preserve complete user/assistant exchanges

### Storage

-   Persistent Chroma database path
-   PDF document location

Centralizing these settings makes experimentation straightforward
without requiring changes throughout the codebase.

------------------------------------------------------------------------

# 🧠 How It Works

The assistant combines a conversational resolution layer with a
registry-driven agentic retrieval workflow.

## Step 1 --- User Question

The CLI accepts a natural-language question and passes it to
`ConversationService`.

## Step 2 --- Conversation Context Resolution

Recent bounded conversation history is supplied to the question rewriter.
The rewriter determines whether the current question has enough context
to be understood.

If a required conversational reference cannot be resolved, retrieval is
skipped and the assistant asks the user to clarify.

## Step 3 --- Standalone Question Rewriting

Resolved follow-up questions are rewritten into standalone retrieval
queries while preserving the user's intent. Standalone questions remain
standalone and avoid an unnecessary rewrite call.

## Step 4 --- Agent Planning

The resolved question is passed to the agent planner.

The planner builds a tool catalog dynamically from the registered tools and
asks the LLM to select the minimum set of tools required to retrieve
evidence. Tool names and capabilities are therefore not hardcoded into the
agent's routing logic.

For current-information questions, the planner can construct a more
explicit time-aware Web query. This behavior is based on tool metadata and
question intent rather than a hardcoded domain such as BERT or PDFs.

## Step 5 --- Tool Validation and Execution

Planner output is parsed and validated against the tool registry.

Unknown tools, malformed arguments, missing required arguments, duplicate
calls, and calls that exceed the configured execution budget are rejected
before execution.

The tool executor resolves the validated call to its registered
implementation and returns a structured observation.

## Step 6 --- Agent Observation Loop

The agent records tool observations and asks the planner whether another
retrieval step is justified.

Follow-up planning is bounded by the configured maximum agent iterations
and per-tool execution limits. Additional retrieval is requested only when
previous evidence is insufficient and another registered tool can
materially improve it.

## Step 7 --- Retrieval Candidate Normalization

Source-specific results become a common application representation:

``` text
PDF Document + Distance ──┐
                           ├──► RetrievalCandidate
Tavily WebResult ─────────┘
```

Each candidate preserves content, source, its original retrieval score,
and citation metadata.

## Step 8 --- Cross-Source Reranking

All candidates are embedded using the same Hugging Face embedding model
and compared with the standalone question using cosine similarity.

PDF distance scores and Tavily relevance scores remain source-specific;
the common reranker provides a separate semantic relevance signal.

## Step 9 --- Top-K Evidence Selection

The strongest reranked candidates are retained according to
`HYBRID_TOP_K`.

When multiple sources contribute evidence, the selection logic ensures
that each contributing source can retain representation before remaining
slots are filled by global semantic relevance.

## Step 10 --- Context Fusion

Ranked PDF and Web evidence is fused into structured context while
preserving source boundaries and citation metadata.

## Step 11 --- Grounded Response Generation

The configured LLM client (direct Groq API or local OmniRoute proxy gateway) generates an answer using only the fused retrieval context.

The generator is instructed not to invent facts or substitute unrelated
evidence. When an important part of the question cannot be established
from the retrieved evidence, the assistant explicitly reports that
limitation instead of guessing.

## Step 12 --- Memory Update

After a resolved interaction completes, the original user question and
generated assistant answer are stored in bounded in-session memory.

Internal rewritten questions are not stored as user messages.

## Step 13 --- Autonomous Multi-Agent Crews & LTM (v3.0.0 addition)

For comprehensive reports, the multi-agent crew executes the full research workflow:
1. **LTM Context Lookup:** The Lead Planner queries the persistent SQLite database for historical files, context overlaps, and user writing/depth preferences.
2. **MCP Connection:** MCP client handshakes with connected stdio tools.
3. **Execution & Synthesis:** Planner, Specialist, and Synthesizer agents execute queries, collect citations, run validation checks, and output a complete formatted Markdown report.
4. **Historical Database Sync:** The final markdown report is automatically recorded to LTM databases for future context recall.

------------------------------------------------------------------------

# 🧪 Testing

The project uses pytest for deterministic unit tests and opt-in external
integration tests.

Run the normal test suite:

``` bash
pytest -v
```

LLM and Tavily tests are skipped by default so normal tests do not
depend on external API calls. To explicitly run all external integration
tests:

``` bash
RUN_LLM_TESTS=true RUN_TAVILY_TESTS=true pytest -v
```

To run tests with active statement coverage reporting:

``` bash
pytest --cov=services --cov=models tests/
```

The v2.6.0 validation suite covers bounded memory behavior,
context-aware question rewriting, unresolved references, conversational
follow-ups, and Tavily result structure/relevance. The v3.0.0 mock suites cover memory tables, MCP, pipeline loaders, rerankers, and fallback overrides.

------------------------------------------------------------------------

# 📦 Release History

  ---------------------------------------------------------------------
  Version                       Description
  ----------------------------- ---------------------------------------
  **v3.0.0**                    Autonomous Multi-Agent Crews, SQLite LTM preference
                                engines, Model Context Protocol stdio dynamic tool
                                integrations, and fallback refusal metadata overrides.

  **v2.9.6**                    OmniRoute AI Gateway integration, OpenAI-compatible
                                client proxying (ChatOpenAI), diagnostic test harness,
                                environment bypass and Pyright warnings resolution.

  **v2.9.5**                    Optimizations & Comparative RAG: document-level source
                                diversity, min relevance thresholds, relative reference
                                pronoun resolution, template prompt compression, collection-aware
                                agent planners, and settings-based evaluator boundaries.

  **v2.9.0**                    Intelligent agent planning, dynamic tool
                                registry, validated tool calls, bounded
                                multi-step execution, observation-driven
                                follow-up planning, improved current Web
                                queries, generic Web search execution, and
                                grounded answer generation.

  **v2.8.0**                    Modular agent architecture, agent state,
                                tool registry, tool runtime, tool execution
                                adapters, PDF and Web knowledge tools, and
                                foundation for agentic retrieval.

  **v2.7.0**                    Multi-collection knowledge bases, dynamic collection
                                discovery, manifest-based index synchronization, and
                                localized vector stores.

  **v2.6.0**                    Bounded in-session conversation memory,
                                context-aware question rewriting,
                                follow-up reference resolution,
                                unresolved-context detection, memory
                                reset, conversation orchestration, and
                                pytest validation.

  **v2.5.0**                    Adaptive hybrid retrieval, normalized
                                cross-source candidates,
                                embedding-based reranking, Top-K
                                evidence selection, context fusion, and
                                hybrid responses.

  **v2.4.0**                    Confidence-based retrieval evaluation,
                                structured response models, citations,
                                clean layered architecture, and
                                improved answer generation.

  **v2.3.0**                    Intelligent PDF-first routing with
                                Tavily web fallback.

  **v2.2.1**                    Centralized environment initialization
                                and startup architecture improvements.

  **v2.2.0**                    Initial stable modular PDF RAG
                                implementation.
  ---------------------------------------------------------------------

------------------------------------------------------------------------

# 🗺️ Roadmap

The long-term goal is to evolve this project into a production-quality
autonomous research assistant.

## ✅ v2.5.0

### Adaptive Hybrid Retrieval

-   True Hybrid Retrieval (PDF + Web)
-   Adaptive PDF-only, Hybrid, and Web-only strategies
-   Shared retrieval candidate representation
-   Embedding-based cross-source reranking
-   Ranked evidence selection
-   Configurable Hybrid Top-K
-   Structured context fusion
-   Hybrid source attribution and citations
-   Combined retrieval confidence policy
-   Simplified hybrid RAG orchestration

------------------------------------------------------------------------

## ✅ v2.6.0

### Conversation Memory & Context-Aware Interactions

-   Bounded in-session conversation memory
-   Typed user and assistant conversation messages
-   Context-aware responses
-   Multi-turn conversations
-   Standalone follow-up question rewriting
-   Pronoun and reference resolution
-   Unresolved-context detection before retrieval
-   Graceful clarification for missing context
-   `clear` command for resetting memory
-   Dedicated conversation orchestration service
-   Unit and external integration testing

------------------------------------------------------------------------

## ✅ v2.7.0

### Multi-Collection Knowledge Base

-   Multiple PDF collections
-   Dynamic collection discovery
-   Automatic document indexing
-   Manifest-based index synchronization
-   Dedicated IndexManager
-   Collection-aware vector databases

------------------------------------------------------------------------

## ✅ v2.8.0

### Agent Architecture & Tool Calling

-   Modular AI Agent architecture
-   Agent state management
-   Tool registry
-   Tool planner
-   Tool runtime
-   Tool execution pipeline
-   PDF knowledge tool
-   Web search tool
-   Knowledge abstraction layer
-   External Tavily web search integration
-   Foundation for ReAct and function calling

------------------------------------------------------------------------

## ✅ v2.9.0

### Intelligent Agentic Retrieval

-   LLM-powered tool selection
-   Dynamic tool registry and capability catalog
-   Validated, registry-driven tool calls
-   Generic tool execution adapters
-   Observation-driven follow-up planning
-   Bounded multi-step agent execution
-   Duplicate-call prevention
-   Per-tool execution limits
-   Improved current-information Web query construction
-   Advanced Tavily search configuration
-   Grounded answer generation with insufficient-evidence handling
-   Extensible architecture for future tools

------------------------------------------------------------------------

## ✅ v2.9.5

### Optimizations & Comparative RAG

-   🏆 Document-level source diversity reranker policies
-   🎯 Configurable evaluation threshold parameters in settings
-   🔗 Relative reference pronoun resolution logic (`one`, `former`, `latter`)
-   ⚡ Prompt instruction token budget reductions (~1500 tokens saved)
-   📂 Collection-aware agent routing (skip redundant vector searches)
-   🧹 Obsolete files housekeeping and cleanup (deleted 6 dead files)

------------------------------------------------------------------------

## ✅ v2.9.6

### OmniRoute AI Gateway Integration

-   🌐 Standard OpenAI-compatible gateway routing (`ChatOpenAI`)
-   🧪 Resolved path namespace 404 bugs via custom base URL configuration
-   🛠️ Centrally managed toggle (`USE_OMNIROUTE`) and API base configs
-   📂 Bypass validator credentials with dummy authentication fallbacks
-   📝 Diagnostic connection testing helper (`scratch/test_omniroute.py`)

------------------------------------------------------------------------

## ✅ v3.0.0

### Autonomous Multi-Agent Research Assistant & Memory

-   🤖 Dynamic planner, researcher, synthesizer multi-agent crews (CrewAI).
-   💾 Persistent Long-Term Memory (LTM) SQLite database.
-   🔌 Model Context Protocol (MCP) dynamic dynamic tool clients.
-   🛡️ Token capacity caps and query constraint overrides.
-   🧪 Mock-based test coverage for all RAG and agent service components.

------------------------------------------------------------------------

# 📚 Learning Journey

This repository serves as a practical exploration of modern AI
application development and software engineering.

Topics covered throughout the project include:

-   Retrieval-Augmented Generation (RAG)
-   Adaptive Hybrid Retrieval
-   Cross-source Reranking
-   Context Fusion
-   Conversation Memory
-   Context-Aware Question Rewriting
-   Multi-Turn Interaction Design
-   Semantic Search
-   Vector Databases
-   Prompt Engineering
-   LangChain & LCEL
-   ChromaDB
-   Confidence-based Retrieval
-   Software Architecture
-   Design Patterns
-   AI Agents
-   Tool Registries and Tool Execution
-   Agent Planning and Observation Loops
-   Model Context Protocol (MCP)

Each release introduces meaningful capabilities while preserving a
clean, maintainable, and extensible architecture.

Rather than rapidly adding features, this project emphasizes **building
AI systems correctly**, ensuring every architectural decision supports
future growth.

------------------------------------------------------------------------

# 🤝 Contributing

Contributions, ideas, and feedback are always welcome.

If you'd like to improve the project, feel free to:

-   ⭐ Star the repository
-   🐛 Report bugs by opening an issue
-   💡 Suggest new features
-   🔧 Submit pull requests
-   📖 Improve the documentation

Whether it's fixing a typo, improving the architecture, or proposing new
AI capabilities, every contribution is appreciated.

------------------------------------------------------------------------

# 📜 License

This project is licensed under the **MIT License**.

Feel free to use, modify, and distribute the project in accordance with
the license terms.

------------------------------------------------------------------------

# ⭐ Support

If you found this project helpful, please consider giving it a ⭐ on
GitHub.

Your support helps others discover the project and motivates continued
development.

------------------------------------------------------------------------

# 👨💻 Author

**Pranjal Agarwal**

AI Engineer passionate about building production-quality AI systems with
a strong emphasis on software architecture, Retrieval-Augmented
Generation (RAG), Agentic AI, and scalable machine learning
applications.

### Connect

-   GitHub: https://github.com/pranjal0203

------------------------------------------------------------------------

# 🙏 Acknowledgements

This project is built using several outstanding open-source
technologies.

Special thanks to the communities behind:

-   LangChain
-   ChromaDB
-   Hugging Face
-   Groq
-   Tavily

Their work makes modern AI application development significantly more
accessible.

------------------------------------------------------------------------

> **"Great AI systems aren't built in a single release---they evolve
> through thoughtful architecture, continuous learning, and disciplined
> engineering."**
