# ADR-001: Migration to CrewAI Multi-Agent Architecture

## Status
Accepted

## Context
In previous versions (up to `v2.9.6`), the assistant relied on a single-agent loop powered by a custom planner template. While functional for single-step retrievals, this architecture struggled with complex research queries that required:
1.  Formulating a multi-stage search query sequence.
2.  Synthesizing structured Markdown reports with explicit citation verification.
3.  Connecting to external Model Context Protocol (MCP) server tools dynamically.

Writing custom state machines, planning loops, and tool execution routines became increasingly complex and hard to maintain.

## Decision
We decided to adopt **CrewAI** as the primary multi-agent orchestration framework for Option 2 Autonomous Research Mode. The single-agent architecture was replaced by three cooperative agents:
*   **Research Planner Agent:** Maps out queries and reviews historical context.
*   **Evidence Retrieval Agent:** Executes Chroma searches, Tavily web searches, and dynamic MCP tools.
*   **Synthesis & Grounding Agent:** Merges retrieved contexts and formats report markdown.

## Consequences

### Positive:
*   **Decoupled Agent Roles:** Each agent operates under a specific backstory and system prompt, resulting in cleaner outputs.
*   **Extensible Tooling:** CrewAI tools are standardized, making it easy to expose custom Python functions or MCP client APIs to the crew.
*   **Cooperative Tasks:** Built-in sequential task delegation allows agents to review each other's outputs.

### Negative:
*   **Higher Token Overhead:** Multi-agent prompts and ReAct loops consume more input tokens.
*   **TPM Sensitive:** Requires strict bounding controls (`max_iter`, length limits) to prevent hitting Groq rate limits.
