"""
CrewAI Multi-Agent Service.

Orchestrates specialized agents (Planner, Researcher, Synthesizer)
to conduct autonomous research and compile structured reports.
"""

from crewai import LLM, Agent, Crew, Task
from crewai.tools import tool


def create_research_tools(vector_store):
    """
    Dynamically construct LangChain tools bound to the active vector_store.
    """

    @tool("search_pdf")
    def search_pdf(query: str) -> str:
        """
        Search the local indexed PDF knowledge base for factual evidence.
        Use for local concepts, definitions, architectures, algorithms,
        findings, methods, or papers in the local document database.
        """
        from services.knowledge.pdf import search_pdf_knowledge

        try:
            results = search_pdf_knowledge(vector_store, query)
            if not results.candidates:
                return "No matching local evidence found."

            # Limit candidates to top 3 and truncate text to prevent token overflow
            evidence = []
            for item in results.candidates[:3]:
                filename = item.citation.title
                content = item.content[:500] if item.content else ""
                evidence.append(f"Source: {filename}\nContent: {content}")
            return "\n\n".join(evidence)
        except Exception as e:  # noqa: BLE001
            return f"Error executing PDF search: {e}"

    @tool("search_web")
    def search_web(query: str) -> str:
        """
        Search the internet for external, current, or time-sensitive information.
        Use when the user explicitly requests recent events, today's news, or external context
        that is not expected to be found in the local document base.
        """
        from services.web_search import search_web as execute_search_web

        try:
            results = execute_search_web(query)
            if not results:
                return "No matching web evidence found."

            # Limit web results to top 2 and truncate text to prevent token overflow
            evidence = []
            for item in results[:2]:
                title = item.title if hasattr(item, "title") else "Web Search Result"
                url = item.url if hasattr(item, "url") else "http://external-source"
                content = item.content[:500] if hasattr(item, "content") else ""
                evidence.append(f"Source: {title} ({url})\nContent: {content}")
            return "\n\n".join(evidence)
        except Exception as e:  # noqa: BLE001
            return f"Error executing Web search: {e}"

    return [search_pdf, search_web]


def run_autonomous_research(topic: str, vector_store) -> str:
    """
    Initialize and run the CrewAI multi-agent research workflow.
    """
    from config.settings import (
        MAX_AGENT_ITERATIONS,
        MODEL_NAME,
        OMNIROUTE_API_BASE,
        TEMPERATURE,
        USE_OMNIROUTE,
    )
    from services.llm import _get_groq_api_key

    # Initialize model target based on configuration
    if USE_OMNIROUTE:
        # Prepend provider prefix so LiteLLM parses it as OpenAI provider
        # but preserves the original provider name in the request payload
        model = MODEL_NAME
        if not model.startswith("openai/"):
            model = f"openai/{model}"
        model = f"openai/{model}"

        crew_llm = LLM(
            model=model,
            base_url=OMNIROUTE_API_BASE,
            api_key=_get_groq_api_key(),
            temperature=TEMPERATURE,
        )
    else:
        # LiteLLM expects a provider prefix for Groq
        model = MODEL_NAME
        if not model.startswith("groq/"):
            model = f"groq/{model}"
        crew_llm = LLM(
            model=model,
            api_key=_get_groq_api_key(),
            temperature=TEMPERATURE,
        )

    # Load SQLite Long-Term Memory (LTM) context
    from services.mcp_client import load_mcp_tools
    from services.memory_service import (
        get_past_context,
        get_preference,
        save_research_report,
    )

    past_context = get_past_context(topic)
    report_style = get_preference("report_style", "professional technical report")
    research_depth = get_preference("research_depth", "comprehensive")

    # Load Model Context Protocol (MCP) server tools
    mcp_tools = load_mcp_tools()

    # 1. Bind tools to active vector store
    tools = create_research_tools(vector_store)
    if mcp_tools:
        tools.extend(mcp_tools)

    # 2. Define specialized Agents
    planner = Agent(
        role="Lead Research Planner",
        goal=(
            f"Analyze the research topic '{topic}', identify key sub-topics to "
            "query, and draft a structured plan of specific search queries to "
            "collect comprehensive evidence."
        ),
        backstory=(
            "An expert research strategist who excels at breaking down "
            "complex topics into targeted informational queries."
        ),
        verbose=True,
        max_iter=MAX_AGENT_ITERATIONS,
        llm=crew_llm,
    )

    researcher = Agent(
        role="Evidence Retrieval Specialist",
        goal=(
            "Execute searches using the search_pdf and search_web tools to "
            "retrieve concrete evidence for each query in the research plan."
        ),
        backstory=(
            "A meticulous search specialist who knows exactly how to query "
            "databases and the web to find precise, raw, factual data."
        ),
        tools=tools,
        verbose=True,
        max_iter=MAX_AGENT_ITERATIONS,
        llm=crew_llm,
    )

    synthesizer = Agent(
        role="Synthesis & Verification Specialist",
        goal=(
            "Compile all retrieved evidence, perform cross-document grounding "
            "checks, draft the final comprehensive report, and cite source "
            "files accurately."
        ),
        backstory=(
            "A senior research synthesizer and editor who compiles disparate "
            "facts into coherent, highly structured reports while maintaining "
            "complete factual integrity."
        ),
        verbose=True,
        max_iter=MAX_AGENT_ITERATIONS,
        llm=crew_llm,
    )

    # Build prompt context blocks dynamically
    context_instruction = ""
    if past_context:
        context_instruction = f"\n\nContext from past research:\n{past_context}"

    pref_instruction = (
        f"\n\nUser Preferences:\n- Depth: {research_depth}\n- Style: {report_style}"
    )

    # 3. Define Tasks
    planning_task = Task(
        description=(
            f"Analyze the research topic: '{topic}'. Identify the key technical aspects, "
            "methods, architectures, or events that need clarification. Output a concise list "
            "of at most 2 or 3 targeted search queries to be run against local files or the web."
            f"{context_instruction}{pref_instruction}"
        ),
        expected_output=(
            "A concise structured list of at most 2 or 3 targeted search queries."
        ),
        agent=planner,
    )

    gathering_task = Task(
        description=(
            "Execute the queries drafted in the research plan. Use search_pdf for "
            "technical details and papers, and search_web for current/external info. "
            "Gather raw, concrete facts, findings, and citations. Keep the raw source "
            "details intact."
        ),
        expected_output=(
            "Raw retrieved paragraphs, search findings, and their respective source "
            "titles/filenames."
        ),
        agent=researcher,
    )

    synthesis_task = Task(
        description=(
            f"Compile all gathered evidence into a comprehensive markdown research report on "
            f"the topic: '{topic}'. The report MUST include:\n"
            "- Executive Summary: A high-level overview of the findings.\n"
            "- Detailed Findings: Deep dives into the key aspects, structured with clear subheadings.\n"
            "- Grounded Citations: Bulleted list of every source file (e.g. [Attention_is_All_You_Need.pdf] "
            "or [Title](URL)) utilized.\n"
            "- Open Questions: Any gaps, missing information, or future areas of study.\n\n"
            "Every claim made in the report must be explicitly cited back to its source (e.g. "
            "'Self-attention allows parallelization [Attention_is_All_You_Need.pdf]')."
        ),
        expected_output="A comprehensive, beautifully formatted markdown research report with grounded inline citations.",
        agent=synthesizer,
    )

    # 4. Form the Crew
    crew = Crew(
        agents=[planner, researcher, synthesizer],
        tasks=[planning_task, gathering_task, synthesis_task],
        verbose=True,
    )

    # 5. Kickoff the process
    result = crew.kickoff()

    report_text = str(result)

    # Save to SQLite memory DB for future context reuse
    save_research_report(topic, report_text)

    # Convert CrewOutput object to string
    return report_text
