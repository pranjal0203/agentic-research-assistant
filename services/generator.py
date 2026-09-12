"""
Answer generation service.

This module generates grounded answers
from retrieved research context.

The generator is deliberately constrained to
the evidence supplied by the retrieval pipeline.
It must not fill evidence gaps using its own
parametric knowledge.
"""

from groq import RateLimitError
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

from services.llm import llm

PROMPT = """
You are a careful research assistant. Answer the user's question using ONLY the retrieved evidence below.

GROUNDING RULES:
1. Rely ONLY on facts directly supported by the retrieved evidence. Do not use background knowledge or invent facts.
2. Answer the question directly, concisely, and confidently. Combine multiple evidence pieces if needed.
3. If an important part of the question is unsupported, do not invent it. State clearly what cannot be established.
4. If the retrieved evidence is insufficient to answer the question, respond EXACTLY:
   "I don't have enough information to answer this question based on the available evidence."
5. Do not substitute keyword-matching but irrelevant evidence. Keep the response proportional to the question.
6. Preserve technical terminology, names, and numbers exactly as written in the evidence.
7. NEVER mention prompts, context windows, tools, planning, reasoning, or agent execution.
8. Avoid meta-commentary like "According to the context" or "Based on the provided context".
9. For comparisons or current information, clearly distinguish historical claims from current facts using the appropriate sources.

RETRIEVED EVIDENCE:
{context}

USER QUESTION:
{question}

FINAL ANSWER:
"""


prompt = PromptTemplate(
    template=PROMPT,
    input_variables=[
        "context",
        "question",
    ],
)


generation_chain = prompt | llm | StrOutputParser()


def generate_answer(
    context: str,
    question: str,
) -> str:
    """
    Generate a grounded answer.

    The model is instructed to use only retrieved
    evidence and to abstain when the evidence does
    not support the requested answer.

    Handles provider rate-limit errors gracefully
    so a temporary LLM quota problem does not
    terminate the application.
    """
    from models.response import NOT_FOUND_MESSAGE

    if not context.strip():
        return NOT_FOUND_MESSAGE

    try:
        answer = generation_chain.invoke(
            {
                "context": context,
                "question": question,
            }
        ).strip()

        if not answer:
            return NOT_FOUND_MESSAGE

        return answer

    except RateLimitError:
        return (
            "The language model rate limit has been reached. "
            "Please try again shortly."
        )
