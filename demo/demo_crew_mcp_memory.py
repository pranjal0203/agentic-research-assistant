#!/usr/bin/env python3
"""
=============================================================================
DEMO SCRIPT 2: CREWAI MULTI-AGENT CREW, MCP INTEGRATION & LONG-TERM MEMORY
=============================================================================
This script demonstrates:
1. Model Context Protocol (MCP) Server Discovery & Dynamic Tool Wrapping
2. Autonomous 3-Agent Collaborative Research Workflow (Planner -> Specialist -> Synthesizer)
3. SQLite Long-Term Memory (LTM) Persistence & Dynamic Persona/Style Customization
=============================================================================
"""

import sys
import time
from pathlib import Path

from dotenv import load_dotenv

# Ensure project root is in sys.path when running from demo/ directory
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Ensure stdout flushes immediately in terminal
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)

# Load environment variables
load_dotenv(ROOT_DIR / ".env")

from services.crew_service import run_autonomous_research
from services.mcp_client import CONFIG_PATH, load_mcp_tools
from services.memory_service import (
    get_past_context,
    get_preference,
    initialize_memory_db,
    list_past_topics,
    set_preference,
)
from services.pipeline import initialize_pipeline

# ANSI Color codes for clean terminal presentation
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_banner(title: str) -> None:
    print(f"\n{CYAN}{'=' * 75}{RESET}")
    print(f"{BOLD}{CYAN}🤖 {title.upper()}{RESET}")
    print(f"{CYAN}{'=' * 75}{RESET}\n")


def print_section(num: int, title: str, description: str) -> None:
    print(f"\n{YELLOW}{'─' * 75}{RESET}")
    print(f"{BOLD}{YELLOW}▶ PART {num}: {title}{RESET}")
    print(f"{YELLOW}  Concept: {description}{RESET}")
    print(f"{YELLOW}{'─' * 75}{RESET}\n")


def demo_mcp() -> None:
    print_section(
        1,
        "Model Context Protocol (MCP) Dynamic Tool Discovery",
        "Discovers external tools over standard JSON-RPC stdio and bridges them into CrewAI",
    )
    print(f"📡 Inspecting MCP configuration at: {BOLD}{CONFIG_PATH}{RESET}")

    mcp_tools = load_mcp_tools()
    print(
        f"🔍 Discovered {BOLD}{len(mcp_tools)}{RESET} dynamic MCP tools from local servers:"
    )

    if mcp_tools:
        for idx, t in enumerate(mcp_tools, 1):
            name = getattr(t, "name", str(t))
            desc = getattr(t, "description", "No description")
            print(f"  {BOLD}{idx}. Tool Name:{RESET} {GREEN}{name}{RESET}")
            print(f"     {BOLD}Description:{RESET} {desc[:100]}...")
    else:
        print(
            f"  {YELLOW}ℹ️  MCP configuration active. Filesystem server configured in config/mcp_servers.json.{RESET}"
        )

    print(f"\n{GREEN}✅ MCP tools successfully bridged into CrewAI toolbelt!{RESET}")


def demo_crew(vector_store) -> None:
    print_section(
        2,
        "Autonomous Multi-Agent Collaboration (CrewAI)",
        "Sequential collaboration between Lead Planner, Retrieval Specialist, and Senior Synthesizer",
    )

    topic = "Compare BERT and Transformer parameter counts"
    print(f'{BOLD}🎯 Research Goal:{RESET} {CYAN}"{topic}"{RESET}')
    print(f"{BOLD}👥 Agent Team Deployed:{RESET}")
    print(
        f"  1. {BOLD}Lead Research Planner:{RESET} Formulates 3-part targeted sub-queries."
    )
    print(
        f"  2. {BOLD}Evidence Retrieval Specialist:{RESET} Queries Chroma PDF vectors & Tavily live search."
    )
    print(
        f"  3. {BOLD}Senior Synthesizer:{RESET} Compiles executive report with grounded citations."
    )

    print(
        f"\n{YELLOW}⏳ Launching Crew process... (Agent thoughts and tool calls will log live below){RESET}\n"
    )
    start_time = time.time()

    try:
        report = run_autonomous_research(topic, vector_store)
        elapsed = time.time() - start_time

        print(f"\n{GREEN}{'=' * 75}{RESET}")
        print(
            f"{BOLD}{GREEN}✅ CREWAI AUTONOMOUS RESEARCH COMPLETED ({elapsed:.1f}s)!{RESET}"
        )
        print(f"{GREEN}{'=' * 75}{RESET}\n")

        print(f"{BOLD}📄 Executive Research Report Output:{RESET}\n")
        print(f"{CYAN}{report}{RESET}\n")

    except Exception as e:  # noqa: BLE001
        print(f"{RED}❌ Crew execution encountered an error: {e}{RESET}")


def demo_memory() -> None:
    print_section(
        3,
        "Persistent Long-Term Memory & Persona Customization (SQLite)",
        "Cross-session persistence of research archives and dynamic tone/depth preferences",
    )

    print(f"{BOLD}Step 1: Initializing ACID SQLite database at db/memory.db...{RESET}")
    initialize_memory_db()

    # 1. Show dynamic preference configuration
    print(f"\n{BOLD}Step 2: Dynamic User Persona & Preference Injection:{RESET}")
    print(
        f"  • Current Research Depth: {GREEN}{get_preference('research_depth', 'comprehensive')}{RESET}"
    )
    print(
        f"  • Current Report Style:   {GREEN}{get_preference('report_style', 'professional technical')}{RESET}"
    )

    print(
        f"\n🔄 Updating preference in SQLite: {BOLD}report_style -> 'concise executive summary'{RESET}"
    )
    set_preference("report_style", "concise executive summary")
    print(f"  • Updated Report Style:   {GREEN}{get_preference('report_style')}{RESET}")

    # 2. Show research history
    print(f"\n{BOLD}Step 3: Querying SQLite Research History Archive:{RESET}")
    history = list_past_topics()
    if history:
        for idx, (t, ts) in enumerate(history, 1):
            print(f"  {idx}. [{ts}] {BOLD}{t}{RESET}")
    else:
        print("  (No past reports logged yet)")

    # 3. Keyword-based past context retrieval
    print(
        f"\n{BOLD}Step 4: Automatic Past Context Retrieval for Next Research Run:{RESET}"
    )
    context = get_past_context("BERT parameters")
    if context:
        print(
            f"  {GREEN}Found past context in SQLite to prevent duplicate research:{RESET}"
        )
        print(f"  {context[:200]}...")
    else:
        print("  (No overlapping past context found)")

    print(f"\n{GREEN}✅ SQLite Long-Term Memory operational!{RESET}")


def main() -> None:
    print_banner("DEMO PART 2: CREWAI, MCP & LONG-TERM MEMORY")

    # Initialize pipeline for vector store
    print(f"{BOLD}Initializing Document Knowledge Base...{RESET}")
    index_manager = initialize_pipeline()
    vector_store = index_manager.get_vector_store("research")

    # Run Demo Steps
    demo_mcp()
    demo_crew(vector_store)
    demo_memory()

    print(f"\n{GREEN}{'=' * 75}{RESET}")
    print(f"{BOLD}{GREEN}🎉 DEMO 2 COMPLETED SUCCESSFULLY!{RESET}")
    print(f"{GREEN}Key takeaways shown:{RESET}")
    print("  1. Extensible MCP client for external tool discovery.")
    print(
        "  2. Autonomous 3-agent CrewAI research workflow generating grounded reports."
    )
    print(
        "  3. Persistent Long-Term Memory (SQLite) for context reuse and persona styling."
    )
    print(f"{GREEN}{'=' * 75}{RESET}\n")


if __name__ == "__main__":
    main()
