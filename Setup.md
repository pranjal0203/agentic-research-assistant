# 🚀 Fresh Laptop Setup Guide: Intelligent Agentic Research Assistant

This guide walks you through setting up, configuring, and running the **Intelligent Agentic Research Assistant** from scratch on a clean/fresh machine (macOS, Linux, or Windows), including local **Docker Desktop** and **OmniRoute AI Gateway** integration.

---

## 📋 Table of Contents
1. [System Prerequisites](#1-system-prerequisites)
   - [Install Git & Python](#install-git--python)
   - [Install Docker Desktop](#install-docker-desktop)
2. [Get Your API Keys](#2-get-your-api-keys)
3. [Clone and Setup Workspace](#3-clone-and-setup-workspace)
4. [Python Environment & Dependencies](#4-python-environment--dependencies)
5. [Configure Environment Variables (`.env`)](#5-configure-environment-variables-env)
6. [OmniRoute AI Gateway Setup (Docker)](#6-omniroute-ai-gateway-setup-docker)
   - [Pull & Start OmniRoute Container](#step-61-pull--start-the-omniroute-docker-container)
   - [Access Dashboard & Register Providers](#step-62-access-dashboard--configure-providers)
   - [Verify Proxy Connectivity](#step-63-test-omniroute-proxy-connectivity)
   - [Useful Docker Management Commands](#step-64-useful-docker-management-commands)
7. [Configure LLM Provider & Routing (`config/settings.py`)](#7-configure-llm-provider--routing-configsettingspy)
8. [Running the Application](#8-running-the-application)
9. [Running Automated Tests](#9-running-automated-tests)
10. [Project Directory Structure](#10-project-directory-structure)
11. [Troubleshooting & FAQs](#11-troubleshooting--faqs)

---

## 1. System Prerequisites

### Install Git & Python

Ensure your new machine has the following foundational tools installed:

- **Git**: [git-scm.com](https://git-scm.com/downloads)
  ```bash
  git --version
  ```
- **Python 3.10 or 3.11** (Python 3.11 is recommended):
  ```bash
  python3 --version
  # or on Windows:
  python --version
  ```

---

### Install Docker Desktop

Docker is required if you want to run the local **OmniRoute AI Gateway** proxy container to manage LLM rate limits, automatic retries, and multi-key load balancing.

* **macOS:**
  1. Download the installer for Apple Silicon (M1/M2/M3/M4) or Intel from [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/).
  2. Or install via Homebrew:
     ```bash
     brew install --cask docker
     ```
  3. Open the **Docker Desktop** application and complete the initial setup.

* **Windows:**
  > ⚠️ **CRITICAL FOR WINDOWS:** You **must** install WSL 2 (Windows Subsystem for Linux) and ensure Hardware Virtualization is enabled in your BIOS. If WSL 2 is missing, Docker Desktop will fail to start and throw a **Virtualization Error** (*"Hardware assisted virtualization and data execution protection must be enabled in the BIOS"* or *"WSL 2 installation is incomplete"*).

  1. **Install WSL 2:** Open **PowerShell as Administrator** and run:
     ```powershell
     wsl --install
     wsl --update
     ```
  2. **Restart your laptop** when prompted by Windows to finalize the WSL 2 installation.
  3. **Verify Virtualization is Enabled:** Open **Task Manager** (`Ctrl + Shift + Esc`) $\rightarrow$ Click **Performance** tab $\rightarrow$ Click **CPU** $\rightarrow$ Verify **Virtualization: Enabled** is displayed in the bottom-right corner. *(If disabled, enable Intel VT-x / AMD-V in your computer's BIOS/UEFI settings).*
  4. **Download & Install Docker Desktop:** Download the Windows installer from [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/) and run the installer.
  5. **Ensure WSL 2 Backend is Active:** In Docker Desktop $\rightarrow$ **Settings** (gear icon) $\rightarrow$ **General** $\rightarrow$ Ensure **"Use the WSL 2 based engine"** is checked.
  6. Verify the Docker whale icon appears running in your taskbar system tray.

* **Linux (Ubuntu / Debian):**
  ```bash
  sudo apt update
  sudo apt install -y docker.io docker-compose
  sudo systemctl start docker
  sudo systemctl enable docker
  sudo usermod -aG docker $USER
  ```

* **Verify Docker is Running:**
  ```bash
  docker --version
  docker ps
  ```

---

## 2. Get Your API Keys

You will need two free API keys to enable the LLM and live web search tools:

1. **Groq Cloud API Key** *(for LLM generation & tool routing)*:
   - Sign up for a free account at [console.groq.com](https://console.groq.com/).
   - Go to **API Keys** $\rightarrow$ Create a key $\rightarrow$ Copy the key (starts with `gsk_...`).
2. **Tavily API Key** *(for live internet search & fallback routing)*:
   - Sign up for a free account at [app.tavily.com](https://app.tavily.com/).
   - Copy your default API key (starts with `tvly-...`).
3. *(Optional)* **Hugging Face Access Token** *(prevents rate limit warnings when downloading embedding model weights)*:
   - Create a free token at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens).

---

## 3. Clone and Setup Workspace

Open your terminal, navigate to your desired directory, and clone the repository:

```bash
git clone https://github.com/pranjal0203/agentic-research-assistant.git
cd intelligent-agentic-research-assistant
```

---

## 4. Python Environment & Dependencies

### Step 4.1: Create a Python Virtual Environment
Creating a virtual environment ensures all libraries remain isolated and don't conflict with system packages.

* **macOS / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```
* **Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
* **Windows (Command Prompt):**
  ```cmd
  python -m venv venv
  venv\Scripts\activate.bat
  ```

*(You will see `(venv)` appear at the start of your terminal prompt indicating the virtual environment is active).*

---

### Step 4.2: Install Required Packages
Upgrade `pip` and install all necessary dependencies (LangChain, ChromaDB, Sentence-Transformers, PyPDF, CrewAI, etc.):

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

*(Note: The initial download includes Hugging Face embedding weights and takes ~1-2 minutes depending on your network speed).*

---

## 5. Configure Environment Variables (`.env`)

Copy the provided template `.env.example` to create your local `.env` file:

```bash
cp .env.example .env
```

Open `.env` in any text editor and paste your credentials:

```env
GROQ_API_KEY=gsk_your_actual_groq_api_key_here
TAVILY_API_KEY=tvly-your_actual_tavily_api_key_here

# Optional:
# HF_TOKEN=hf_your_actual_token_here
```

> ⚠️ **Important:** The `.env` file is already listed in `.gitignore` so your private API keys will never be accidentally pushed to Git.

---

## 6. OmniRoute AI Gateway Setup (Docker)

**OmniRoute** is an AI proxy gateway that runs locally to handle automatic model routing, rate-limit bypassing, request logging, and multi-provider failover.

### Step 6.1: Pull & Start the OmniRoute Docker Container

Make sure **Docker Desktop** is running, then execute:

```bash
docker run -d \
  -p 20128:20128 \
  -v omniroute-data:/app/data \
  --name omniroute \
  --restart unless-stopped \
  diegosouzapw/omniroute:latest
```

* **Image:** `diegosouzapw/omniroute:latest`
* **Port Mapping:** `-p 20128:20128` (Exposes the dashboard & OpenAI-compatible proxy API on port `20128`)
* **Data Volume:** `-v omniroute-data:/app/data` (Persists your credentials and routes across container restarts)
* **Container Name:** `--name omniroute`

---

### Step 6.2: Access Dashboard & Configure Providers

1. Open your web browser and navigate to:
   👉 **`http://localhost:20128`**
2. Log in using the default administrator credentials:
   * **Username:** `admin`
   * **Password:** `CHANGEME`
3. *(Recommended)* Change your default password under Settings / Security.
4. Go to **Providers** in the sidebar:
   * Click **Add Provider** $\rightarrow$ Select **Groq** (or OpenAI / Anthropic).
   * Paste your `GROQ_API_KEY` (`gsk_...`).
   * Save the provider.
5. In **Models / Routes**:
   * Ensure model aliases (e.g. `openai/gpt-oss-120b` or `llama-3.3-70b-versatile`) are mapped to your active Groq credentials.

---

### Step 6.3: Test OmniRoute Proxy Connectivity

Run the included verification script to ensure your local Python application can communicate with OmniRoute on port `20128`:

```bash
PYTHONUNBUFFERED=1 PYTHONPATH=. ./venv/bin/python scratch/test_omniroute.py
```

If configured properly, it will print a successful model generation response!

---

### Step 6.4: Useful Docker Management Commands

| Action | Command |
| :--- | :--- |
| **Check container status** | `docker ps -a --filter name=omniroute` |
| **View live logs** | `docker logs -f omniroute` |
| **Stop container** | `docker stop omniroute` |
| **Start stopped container** | `docker start omniroute` |
| **Restart container** | `docker restart omniroute` |

---

## 7. Configure LLM Provider & Routing (`config/settings.py`)

Open `config/settings.py` to toggle between **Direct Groq Cloud Mode** and **Local OmniRoute Gateway Mode**:

```python
# ============================================================
# Mode A: Direct Groq Cloud (No Docker required)
# ============================================================
USE_OMNIROUTE = False
MODEL_NAME = "llama-3.3-70b-versatile"  # or "llama3-8b-8192"

# ============================================================
# Mode B: Local OmniRoute Gateway (Requires Docker container running)
# ============================================================
USE_OMNIROUTE = True
MODEL_NAME = "openai/gpt-oss-120b"
OMNIROUTE_API_BASE = "http://localhost:20128/v1"
```

* **Embedding Model Setting:** 
  The default embedding model is set to `"BAAI/bge-small-en-v1.5"`:
  ```python
  EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
  ```

---

## 8. Running the Application

Make sure your virtual environment is active (`source venv/bin/activate`), then start the application:

```bash
python app.py
```

### Initial Run & Collection Selection
1. On initial startup, the application discovers all folders inside `data/`:
   ```text
   📂 Discovering document collections...
   ✅ Pipeline initialized.

   📚 Available collections:
   1. finance (1 documents)
   2. legal (1 documents)
   3. medical (2 documents)
   4. research (3 documents)

   Select a collection: 4
   ```
2. Type `4` and press Enter to select the **`research`** collection *(which includes `Attention_is_All_You_Need.pdf`, `BERT.pdf`, and `NEURAL_MACHINE_TRANSLATION.pdf`)*.
3. The embedding engine will vectorize and store the document chunks in `db/research_vector_store`.

---

### Interactive Main Menu Walkthrough

```text
🤖 Intelligent Agentic Research Assistant
📚 Active Collection: research
------------------------------------------
1. Start Interactive Q&A Chat Session
2. Start Autonomous Research & Report Generation (v3.0.0)
3. View Past Research Reports Logs (LTM)
4. Update Research Style Preferences (LTM)
5. Change Document Collection
6. Rebuild Current Collection Index
7. Clear Conversational Memory
8. Exit
------------------------------------------
```

| Option | Feature | Description |
| :--- | :--- | :--- |
| **`1`** | **Conversational RAG Chat** | Multi-turn conversational Q&A with pronoun resolution, citation tracking, and dynamic fallback to Tavily live web search. Type `exit` to return to menu or `clear` to reset chat memory. |
| **`2`** | **Autonomous Research Crew** | CrewAI multi-agent team (Planner, Specialist, Synthesizer) performs deep research on a topic, compiles a structured report, and saves it to `outputs/`. |
| **`3`** | **View Past Reports (LTM)** | Reads and displays previously generated research reports from SQLite database (`db/memory.db`). |
| **`4`** | **Update Preferences (LTM)** | Adjusts agent tone, output depth (`brief` / `detailed` / `comprehensive`), and style (`technical` / `concise`) stored in SQLite memory. |
| **`5`** | **Change Collection** | Switch between `finance`, `legal`, `medical`, and `research` collections on the fly. |
| **`6`** | **Rebuild Index** | Force-deletes existing vector database cache and re-indexes the collection from raw PDF documents. |
| **`7`** | **Clear Memory** | Clears short-term conversational message history buffer. |
| **`8`** | **Exit** | Cleanly terminates the application session. |

---

## 9. Running Automated Tests

Run the full pytest suite to verify all 25 unit tests pass on your machine:

```bash
pytest
```

Run tests with verbose output:
```bash
pytest -v
```

Run a specific test module:
```bash
pytest tests/test_agent_workflow.py -v
```

---

## 10. Project Directory Structure

```text
intelligent-agentic-research-assistant/
├── app.py                      # Main Interactive CLI Application Entry Point
├── config/
│   └── settings.py             # Global constants, LLM & embedding configurations
├── data/                       # Local document repositories by category
│   ├── finance/
│   ├── legal/
│   ├── medical/
│   └── research/               # Attention Is All You Need, BERT, NMT PDFs
├── db/                         # Persistent storage (Chroma Vector DBs & SQLite memory.db)
├── models/                     # Strongly-typed Pydantic & dataclass domain models
├── services/                   # Core pipeline & agent services
│   ├── agent.py                # ReAct orchestrator loop
│   ├── agent_planner.py        # Planning & tool selection interface
│   ├── tool_selector.py        # Routing mini-agent (PDF vs Web search selection)
│   ├── question_rewriter.py    # Multi-turn context resolution & query rewriter
│   ├── retriever.py            # ChromaDB vector retrieval & MMR search
│   ├── reranker.py             # Cosine similarity reranker
│   ├── generator.py            # Grounded generation with citation synthesis
│   ├── crew_service.py         # CrewAI autonomous multi-agent research workflow
│   └── memory_service.py       # SQLite Long-Term Memory (LTM) database operations
├── study_guides/               # Presentation & concept study guides (viewer.html)
├── tests/                      # Automated unit test suite (25 test cases)
├── .env.example                # Sample environment file template
├── requirements.txt            # Python dependencies
└── Setup.md                    # This setup guide
```

---

## 11. Troubleshooting & FAQs

### Q1: Warning: "You are sending unauthenticated requests to the HF Hub"
* **Explanation:** Hugging Face issues a mild warning when downloading open weights anonymously.
* **Fix:** You can safely ignore this. If you want faster download speeds or to suppress the message, generate a free token at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) and add `HF_TOKEN=hf_...` in your `.env` file.

---

### Q2: Error connecting to `http://localhost:20128/v1` (OmniRoute Gateway)
* **Explanation:** `config/settings.py` has `USE_OMNIROUTE = True`, but the local Docker container is not running on your new laptop.
* **Fix:** Either:
  1. Open `config/settings.py` and set `USE_OMNIROUTE = False` to call Groq directly over the cloud.
  2. Or start your local OmniRoute docker container on port `20128` (`docker start omniroute`).

---

### Q3: Port 20128 is already allocated
* **Explanation:** Another service or an old OmniRoute instance is using port 20128.
* **Fix:** Check running containers with `docker ps` and stop the conflicting container with `docker stop <container_id>`.

---

### Q4: How do I force re-index after adding new PDFs?
* **Fix:** Launch `python app.py` and choose **Option 6 (Rebuild Current Collection Index)**. Alternatively, you can delete the corresponding folder inside `db/` (e.g. `rm -rf db/research_vector_store`) and restart `app.py`.

---

### Q5: Pytest shows warnings for CrewAI / function calling
* **Explanation:** CrewAI internal deprecation warnings for future version upgrades.
* **Fix:** These warnings are harmless and can be ignored. All tests pass with exit code `0`.

---

### Q6: Windows Docker Error: "Virtualization error" / "WSL 2 installation is incomplete"
* **Explanation:** Occurs on Windows when Docker Desktop cannot find a functioning WSL 2 Linux kernel or if CPU hardware virtualization is disabled in the BIOS.
* **Fix:**
  1. Open PowerShell as Administrator and run:
     ```powershell
     wsl --install
     wsl --update
     wsl --set-default-version 2
     ```
  2. Reboot your computer.
  3. If the error persists, enter your laptop's BIOS/UEFI on reboot (usually `F2`, `F10`, or `Del`) and enable **Intel Virtualization Technology (VT-x)** or **AMD-V (SVM Mode)**.

---

🎉 **You are all set! Happy Researching!**
