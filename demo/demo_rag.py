#!/usr/bin/env python3
"""
=============================================================================
DEMO SCRIPT 1: CONVERSATIONAL RAG, PRONOUN REWRITING & GUARDRAILS
=============================================================================
This script demonstrates:
1. Document Ingestion & Chroma Vector DB Indexing
2. Multi-turn Conversational RAG with Contextual Pronoun Resolution
3. Hallucination Refusal Guardrails on gibberish/out-of-scope input
4. Dynamic Web Search Fallback (Tavily) for time-sensitive queries
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

from config.settings import MAX_CONVERSATION_MESSAGES
from services.conversation import ConversationService
from services.conversation_memory import ConversationMemory
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
    print(f"{BOLD}{CYAN}🚀 {title.upper()}{RESET}")
    print(f"{CYAN}{'=' * 75}{RESET}\n")


def print_scenario(num: int, title: str, description: str) -> None:
    print(f"\n{YELLOW}{'─' * 75}{RESET}")
    print(f"{BOLD}{YELLOW}▶ SCENARIO {num}: {title}{RESET}")
    print(f"{YELLOW}  Concept: {description}{RESET}")
    print(f"{YELLOW}{'─' * 75}{RESET}")


def execute_turn(conversation: ConversationService, query: str) -> None:
    print(f'\n{BOLD}👤 User Query:{RESET} {CYAN}"{query}"{RESET}')
    start_time = time.time()

    response = conversation.ask(query)
    elapsed = time.time() - start_time

    if response:
        print(f"\n{BOLD}🤖 Assistant Answer:{RESET}\n{response.answer}\n")
        print(f"{BOLD}📊 Verification Metadata:{RESET}")
        print(f"  • {BOLD}Source:{RESET}     {GREEN}{response.source.value}{RESET}")
        print(f"  • {BOLD}Confidence:{RESET} {GREEN}{response.confidence.value}{RESET}")
        citations = (
            [c.title for c in response.citations] if response.citations else ["None"]
        )
        print(f"  • {BOLD}Citations:{RESET}  {MAGENTA}{citations}{RESET}")
        print(f"  • {BOLD}Latency:{RESET}    {elapsed:.2f}s")
    else:
        print(f"{RED}❌ No response returned.{RESET}")


def main() -> None:
    print_banner("DEMO PART 1: CONVERSATIONAL RAG & DYNAMIC ROUTING")

    # 1. Pipeline Initialization
    print(f"{BOLD}Step 1: Initializing Ingestion Pipeline & Vector Stores...{RESET}")
    index_manager = initialize_pipeline()
    collection_name = "research"

    print(
        f"📂 Loading Vector Store for collection: {BOLD}{collection_name}{RESET} "
        "(Attention Is All You Need + BERT)"
    )
    vector_store = index_manager.get_vector_store(collection_name)

    # Initialize Memory & Conversation Service
    memory = ConversationMemory(max_messages=MAX_CONVERSATION_MESSAGES)
    conversation = ConversationService(vector_store=vector_store, memory=memory)
    print(f"{GREEN}✅ Conversational RAG Engine ready!{RESET}\n")

    # -------------------------------------------------------------------------
    # Scenario 1: Standard Domain Question (Vector Search + Reranker)
    # -------------------------------------------------------------------------
    print_scenario(
        1,
        "Direct Document Grounding",
        "Chroma vector search + Cosine Reranking against Attention Is All You Need PDF",
    )
    execute_turn(conversation, "What is self-attention?")

    # -------------------------------------------------------------------------
    # Scenario 2: Conversational Follow-up (Pronoun Resolution)
    # -------------------------------------------------------------------------
    print_scenario(
        2,
        "Contextual Pronoun Resolution",
        "Resolves pronoun 'it' -> 'self-attention' using sliding-window conversation memory",
    )
    execute_turn(conversation, "Why is it useful?")

    # -------------------------------------------------------------------------
    # Scenario 3: Hallucination & Refusal Guardrail
    # -------------------------------------------------------------------------
    print_scenario(
        3,
        "Zero-Hallucination Refusal Guard",
        "Detects unanswerable/gibberish input and strictly refuses to fabricate facts",
    )
    execute_turn(conversation, "aksaksamcaksc")

    # -------------------------------------------------------------------------
    # Scenario 4: Dynamic Web Search Fallback
    # -------------------------------------------------------------------------
    print_scenario(
        4,
        "External Time-Sensitive Fallback",
        "Router detects query is not in PDF collection and dynamically invokes Tavily Web Search",
    )
    execute_turn(conversation, "Who won FIFA World Cup 2026?")

    # -------------------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------------------
    print(f"\n{GREEN}{'=' * 75}{RESET}")
    print(f"{BOLD}{GREEN}🎉 DEMO 1 COMPLETED SUCCESSFULLY!{RESET}")
    print(f"{GREEN}Key takeaways shown:{RESET}")
    print("  1. Grounded RAG with strict page/document citations.")
    print("  2. Multi-turn pronoun resolution across turns without user repetition.")
    print("  3. Robust hallucination refusal protection.")
    print("  4. Dynamic local-to-web tool routing.")
    print(f"{GREEN}{'=' * 75}{RESET}\n")


if __name__ == "__main__":
    main()
