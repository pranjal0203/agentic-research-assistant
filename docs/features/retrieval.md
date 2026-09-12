# 🔀 Hybrid Retrieval, Reranking, & Fusion

This document details the multi-source retrieval pipeline, semantic reranking policies, and citation preservation.

---

## 📄 1. Local Vector Search (Chroma DB)
Local documents are stored inside subdirectories of `data/` (e.g. `data/research/`).
*   **Vector Database:** Managed by `langchain_chroma`.
*   **Chunk Splitting:** Documents are split into segments of `1200` characters.
*   **Embeddings:** Hugging Face `SentenceTransformerEmbeddings` (`all-MiniLM-L6-v2`) generate 384-dimensional vector weights.

---

## 🌐 2. External Web Search (Tavily)
*   **Client:** `TavilyClient` handles search routing.
*   **Mode:** Uses `search_depth="advanced"` to fetch high-authority web targets.
*   **Result Structure:** Returns normalized title, URL, and description snippets.

---

## 🏆 3. Cross-Source Reranking
Chroma DB distances (L2 metrics) and Tavily search relevance scores have different scales. To rank them fairly, we embed the user query and all candidate texts using the *same* embeddings model and calculate cosine similarity:

$$\text{Relevance Score} = \cos(\theta) = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\| \|\mathbf{v}\|}$$

Candidates are sorted globally by this score.

---

## 🧬 4. Document Diversity Protection
To prevent a single document from dominating the context window and pushing out other relevant sources:
1.  **Grouping:** Candidates are grouped by their source file title (e.g. `BERT.pdf`, `Attention.pdf`, `Web`).
2.  **Diversity Sort:** The top representative of *each* unique document is moved to the front of the list.
3.  **Slicing:** We slice the top candidates to fit `HYBRID_TOP_K` settings. This ensures multi-document representation for comparative queries (e.g. *"Compare BERT parameters with Transformer parameters"*).
