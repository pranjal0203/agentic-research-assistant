# 📖 Codebase Documentation Index

Welcome to the documentation portal. This directory contains detailed architectural guides, setup manuals, features specifications, and architectural decision records (ADRs) to help you understand every aspect of the project.

---

## 🗺️ Documentation Map

| Section | Document | Purpose |
| :--- | :--- | :--- |
| **Architecture** | [system.md](architecture/system.md) | Dual-mode execution flows & Mermaid.js sequence diagrams |
| | [components.md](architecture/components.md) | Sub-system component contracts, interfaces, and classes |
| | [codebase-map.md](architecture/codebase-map.md) | File dependency mappings and import structures |
| **Development** | [setup.md](development/setup.md) | Onboarding instructions, virtual environments, & API credentials |
| | [configuration.md](development/configuration.md) | Matrix of settings parameters inside settings.py |
| | [testing.md](development/testing.md) | Guide to running mock unit tests and coverage metrics |
| **Features** | [agents.md](features/agents.md) | Multi-agent configurations, prompts, and token safety caps |
| | [memory.md](features/memory.md) | SQLite Long-Term Memory DDL schemas & preference settings |
| | [retrieval.md](features/retrieval.md) | ChromaDB vector searches, Tavily search, and fusion reranking |
| **Decisions (ADRs)** | [ADR-001-CrewAI.md](decisions/ADR-001-CrewAI.md) | Rationale behind migrating from single to multi-agent crews |
| | [ADR-002-SQLite-LTM.md](decisions/ADR-002-SQLite-LTM.md) | Rationale behind choosing local SQLite databases for LTM |
| **Reference** | [faq.md](reference/faq.md) | Troubleshooting guides, rate limit details, and MCP setups |

---

## 🚀 Getting Started

If you are new here:
1. Start with the [Setup Guide](development/setup.md) to initialize your environment.
2. Read the [System Architecture Guide](architecture/system.md) to understand the runtime execution flows.
3. Explore the [Codebase Map](architecture/codebase-map.md) to locate specific files.
