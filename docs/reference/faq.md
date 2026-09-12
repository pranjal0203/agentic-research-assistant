# ❓ Frequently Asked Questions (FAQ) & Troubleshooting

This document addresses common questions and troubleshooting steps for the Research Assistant.

---

## ⚡ API Rate Limits & Groq TPM Issues

### Q: Why do I see "RateLimitError" or "TPM Limit Exceeded"?
**A:** Groq’s free tier enforces strict limits on Tokens Per Minute (TPM). Multi-agent ReAct loops can easily exceed these limits because they accumulate context with every step.

#### Solutions:
1.  **Lower Agent Iterations:** Verify that `MAX_AGENT_ITERATIONS` in `config/settings.py` is set to `3`.
2.  **Use OmniRoute AI Gateway:** Spin up a local OmniRoute proxy to round-robin requests across multiple API keys. Enable the proxy by setting `USE_OMNIROUTE = True` in `config/settings.py`.
3.  **Reduce Reranking context:** Set `HYBRID_TOP_K = 3` to send fewer text segments to the generator.

---

## 🔌 Model Context Protocol (MCP) Issues

### Q: The specialist agent fails to load MCP tools. Why?
**A:** This typically happens when the subprocess command cannot run or path arguments are invalid.

#### Troubleshooting:
1.  Open [`config/mcp_servers.json`](file:///Users/pranjalagarwal/Downloads/agentic-research-assistant/config/mcp_servers.json).
2.  Verify the server executable path. If using a Node-based tool, ensure node is installed (`node -v`) and the absolute path to the script is correct.
3.  Look at the console output logs. If the subprocess exits prematurely, the client will catch the error and fall back to native tools (Chroma/Tavily) without crashing.

---

## 📁 Local Vector Store Rebuilding

### Q: I added a new PDF to my collection folder, but the assistant doesn't know about it. Why?
**A:** The Index Manager caches index states using a manifest file. If a new document is added, it should be detected automatically on app start. If not:
1.  Navigate to your workspace directory.
2.  Delete the corresponding Chroma database subfolder inside `db/` (e.g. `db/research`).
3.  Rerun `python app.py` and select the collection number again. The index manager will rebuild the vector index.
