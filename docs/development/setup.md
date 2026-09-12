# 🚀 Setup & Installation Guide

This document provides step-by-step instructions to set up the codebase locally.

---

## 📋 Prerequisites
*   **Python:** Version `3.11` or `3.12`.
*   **Node.js (Optional):** Required if running filesystem MCP servers.
*   **Git:** To clone the repository.

---

## 🛠️ Step-by-Step Installation

### Step 1: Clone the Repository
```bash
git clone https://github.com/pranjal0203/agentic-research-assistant.git
cd intelligent-agentic-research-assistant
```

### Step 2: Create a Virtual Environment

#### macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Windows:
```powershell
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

---

## ⚙️ Environment Variables

Create a file named `.env` in the root of the repository:

```env
# Groq API key for LLM generation
GROQ_API_KEY=gsk_your_groq_api_key

# Tavily API key for web search retrieval
TAVILY_API_KEY=tvly-your_tavily_api_key

# Optional: LangSmith tracking parameters
LANGCHAIN_TRACING_V2=false
LANGCHAIN_API_KEY=your_langchain_api_key
```

---

## 📦 Running the Application

1.  **Launch the interactive CLI:**
    ```bash
    python app.py
    ```
2.  Follow the console prompts:
    *   Select a collection folder (e.g. `4. research`) to index documents.
    *   Input numbers 1-8 to navigate between Conversational RAG, Autonomous Crew Research, LTM logs, and Preferences editor.
