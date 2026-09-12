# ⚙️ Application Configurations

All application settings are isolated in a single configuration file [`config/settings.py`](file:///Users/pranjalagarwal/Downloads/agentic-research-assistant/config/settings.py).

---

## 🛠️ Configuration Parameter Matrix

| Parameter | Type | Default Value | Description |
| :--- | :--- | :--- | :--- |
| **`DATA_DIR_PATH`** | `str` | `"data"` | Folder path where local PDF collection folders reside. |
| **`CHROMA_DB_PATH`** | `str` | `"db"` | Folder path where persistent Chroma vector stores are saved. |
| **`CHUNK_SIZE`** | `int` | `1200` | Size of document text segments in characters when indexing. |
| **`CHUNK_OVERLAP`** | `int` | `200` | Overlap character size between adjacent text chunks. |
| **`EMBEDDING_MODEL_NAME`** | `str` | `"all-MiniLM-L6-v2"` | Hugging Face model identifier for generating vector embeddings. |
| **`RETRIEVAL_TOP_K`** | `int` | `10` | Number of raw document chunks to fetch from Chroma DB. |
| **`HYBRID_TOP_K`** | `int` | `5` | Maximum number of merged candidates sent to the final generator context. |
| **`MIN_SOURCE_RELEVANCE`** | `float` | `0.40` | Similarity score threshold to accept a candidate chunk. |
| **`LLM_MODEL_NAME`** | `str` | `"llama-3.1-70b-versatile"` | Default LLM model used for generation tasks. |
| **`MAX_AGENT_ITERATIONS`** | `int` | `3` | Maximum ReAct loop steps allowed before halting. |
| **`MAX_CONVERSATION_MESSAGES`**| `int` | `6` | Memory window capacity limit for conversational chat. |
| **`USE_OMNIROUTE`** | `bool` | `False` | Toggle to route requests through local OmniRoute API gateway proxy. |
| **`OMNIROUTE_API_BASE`** | `str` | `"http://localhost:20128/v1"` | Connection endpoint URL for local OmniRoute proxy. |

---

## 🔍 Fine-Tuning Relevance Scores

If the RAG response frequently claims *"I don't have enough information"* for questions you know are in the PDF:
1. Open `config/settings.py`.
2. Lower `MIN_SOURCE_RELEVANCE` (e.g., from `0.40` to `0.30`) to allow weaker semantic matches to pass filters.
3. Raise `RETRIEVAL_TOP_K` to fetch a wider range of document chunks.
