"""
Context-aware question rewriting service.

This module resolves conversational questions
and rewrites them into standalone retrieval
questions.

The rewriter is domain-agnostic. It does not
contain knowledge about PDFs, BERT, research
topics, or any particular retrieval source.
"""

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

from models.conversation_message import ConversationMessage
from models.rewrite_result import RewriteResult
from services.llm import llm

REWRITE_PROMPT = """
You are a question rewriting component of an
agentic research assistant.

Your ONLY job is to convert the user's current
question into a standalone question suitable
for retrieval.

You must NOT answer the question.

You must NOT perform retrieval.

You must NOT select tools.

You must NOT add facts that are not supported
by the conversation.

==================================================
CORE PRINCIPLE
==================================================

A question is standalone when its meaning can be
understood without previous conversation context.

A question is contextual when its meaning depends
on something established earlier in the conversation.

When a question is contextual, resolve it using
the MOST RECENT relevant information in the
conversation.

Do not resolve a reference using an older topic
when a newer, more relevant topic exists.

==================================================
STANDALONE QUESTIONS
==================================================

If the question is already understandable on its
own, always return:

RESOLVED: YES
QUESTION: <same question>

Examples:

Current question:
What is BERT?

RESOLVED: YES
QUESTION: What is BERT?

Current question:
What is BERTBASE?

RESOLVED: YES
QUESTION: What is BERTBASE?

Current question:
Who is the current CEO of OpenAI?

RESOLVED: YES
QUESTION: Who is the current CEO of OpenAI?

Current question:
What is positional encoding?

RESOLVED: YES
QUESTION: What is positional encoding?

Current question:
How does BERT compare with current language models?

RESOLVED: YES
QUESTION: How does BERT compare with current language models?

==================================================
CONTEXTUAL QUESTIONS
==================================================

Resolve references when the conversation provides
a clear antecedent.

Examples:

Conversation:
User: What is BERT?
Assistant: BERT is a language representation model.

Current question:
What about its architecture?

Return:

RESOLVED: YES
QUESTION: What is the architecture of BERT?

---

Conversation:
User: What is BERT?
Assistant: BERT is a language representation model.

Current question:
How many layers does it have?

Return:

RESOLVED: YES
QUESTION: How many layers does BERT have?

---

Conversation:
User: What is BERT?
Assistant: BERT has two model sizes, a smaller
version and a larger version.

Current question:
What about the larger version?

Return a standalone question referring to
the previously established subject and preserve
the user's intent.

For example:

RESOLVED: YES
QUESTION: What is the larger version of BERT?

---

Conversation:
User: What is BERT?
Assistant: BERT has two model sizes.

User: What about the larger version?
Assistant: The larger version has more parameters.

Current question:
How many parameters does it have?

The phrase "it" refers to the most recently
discussed larger version.

Return:

RESOLVED: YES
QUESTION: How many parameters does the larger version of BERT have?

---

Conversation:
User: What is BERT?
Assistant: BERT has BERTBASE and BERTLARGE.

User: What about BERTLARGE?
Assistant: BERTLARGE has more layers.

Current question:
How many parameters does it have?

Return:

RESOLVED: YES
QUESTION: How many parameters does BERTLARGE have?

==================================================
REFERENCE TYPES
==================================================

Treat the following as potentially contextual:

Pronouns:
- it
- its
- they
- them
- their
- this
- that
- these
- those

Conversational phrases:
- what about ...
- how about ...
- what about the larger version
- what about the smaller version
- what about the previous one
- what about the other one
- what about the above
- what about the same thing
- how does it ...
- how is it ...
- why does it ...
- why is it ...
- how many does it have
- how much does it have
- what does it use
- what does it mean
- what are its ...
- what is its ...

Comparative or relational references:
- larger version
- smaller version
- previous version
- next version
- other version
- former
- latter
- same
- another
- this model
- that model
- the model
- this paper
- that paper
- the paper
- this architecture
- that architecture
- the architecture
- this method
- that method
- the method
- this approach
- that approach
- the approach

These are examples of contextual language,
not fixed domain-specific rules.

==================================================
LATEST RELEVANT ENTITY
==================================================

When resolving a contextual question, identify
the most recent entity or subject that the user
and assistant were discussing.

Example:

User:
What is BERT?

Assistant:
BERT has BERTBASE and BERTLARGE.

User:
What about BERTLARGE?

Assistant:
BERTLARGE has 24 layers.

User:
How many parameters does it have?

The answer must refer to BERTLARGE, not BERT
generally.

Therefore:

RESOLVED: YES
QUESTION: How many parameters does BERTLARGE have?

==================================================
PRESERVE USER INTENT
==================================================

Do not change what the user is asking.

For example:

"What about its architecture?"

means:

"What is the architecture of <resolved entity>?"

It does NOT mean:

"Explain everything about <resolved entity>."

Likewise:

"How many parameters does it have?"

must remain a parameter question.

Do not turn it into a general description.

==================================================
DO NOT INVENT FACTS
==================================================

You may use entity names, subjects, relationships,
and facts that are explicitly present in the
conversation.

Do not introduce information from your own
knowledge.

For example, if the conversation mentions:

"Model A has a larger version called Model B."

You may rewrite:

"What about the larger version?"

as:

"What is the larger version of Model A?"

But you must not introduce another model name
that was never mentioned.

==================================================
WHEN CONTEXT IS INSUFFICIENT
==================================================

If the current question requires conversation
context but the conversation does not contain
enough information to resolve it, return:

RESOLVED: NO
QUESTION:

Examples:

Current question:
What about that?

No conversation history.

Return:

RESOLVED: NO
QUESTION:

---

Conversation:
User: We discussed several models.

Current question:
How many parameters does it have?

If there is no clear entity to which "it" refers:

RESOLVED: NO
QUESTION:

==================================================
IMPORTANT DISTINCTION
==================================================

Do NOT mark a question unresolved simply because
it contains conversational wording.

If the conversation clearly resolves the reference,
rewrite it.

Do NOT mark a standalone question unresolved merely
because there is no conversation history.

==================================================
OUTPUT FORMAT
==================================================

Return EXACTLY two lines.

RESOLVED: YES or NO
QUESTION: <standalone question>

Do not output explanations.

Conversation history:
{history}

Current question:
{question}
"""


rewrite_prompt = PromptTemplate(
    template=REWRITE_PROMPT,
    input_variables=[
        "history",
        "question",
    ],
)

rewrite_chain = rewrite_prompt | llm | StrOutputParser()


def build_conversation_history(
    messages: list[ConversationMessage],
) -> str:
    """
    Convert conversation messages into
    text suitable for the rewriting prompt.

    The complete available conversation history
    is preserved so the LLM can resolve references
    across multiple turns.
    """

    if not messages:
        return "No conversation history."

    return "\n".join(
        (f"{message.role.value.capitalize()}: " f"{message.content}")
        for message in messages
    )


def _parse_rewrite_result(
    output: str,
    original_question: str,
) -> RewriteResult:
    """
    Parse the LLM rewriting response.

    If the response format is malformed,
    preserve the original question rather
    than blocking retrieval.
    """

    resolved: bool | None = None
    rewritten_question = ""

    for line in output.strip().splitlines():
        key, separator, value = line.partition(":")

        if not separator:
            continue

        key = key.strip().upper()
        value = value.strip()

        if key == "RESOLVED":
            if value.upper() == "YES":
                resolved = True

            elif value.upper() == "NO":
                resolved = False

        elif key == "QUESTION":
            rewritten_question = value

    # Fail open for malformed output.
    #
    # The original question is still a valid
    # retrieval question in most cases.
    if resolved is None:
        return RewriteResult(
            question=original_question,
            resolved=True,
        )

    if not resolved:
        return RewriteResult(
            question=original_question,
            resolved=False,
        )

    return RewriteResult(
        question=rewritten_question or original_question,
        resolved=True,
    )


REFERENCE_PRONOUNS = {
    "it",
    "its",
    "they",
    "them",
    "their",
    "this",
    "that",
    "these",
    "those",
    "he",
    "him",
    "his",
    "she",
    "her",
    "hers",
    "one",
    "ones",
    "former",
    "latter",
}

CONTEXTUAL_PHRASES = (
    "what about",
    "how about",
    "what does it",
    "what is its",
    "what are its",
    "how does it",
    "how is it",
    "why does it",
    "why is it",
    "how many does it",
    "how much does it",
    "what does this",
    "what does that",
    "how does this",
    "how does that",
    "why does this",
    "why does that",
    "the model",
    "the paper",
    "the architecture",
    "the author",
    "the method",
    "the approach",
    "the larger version",
    "the smaller version",
    "the previous version",
    "the next version",
    "the other version",
    "the previous one",
    "the next one",
    "the other one",
    "the same",
    "another one",
    "the above",
    "the latter",
    "the former",
)


def _contains_reference_pronoun(
    question: str,
) -> bool:
    """
    Determine whether the question contains
    a pronoun that may require conversational
    context.

    Whole-word matching prevents false positives
    such as "item" matching "it".
    """

    tokens = {
        token.strip(
            ".,!?;:()[]{}\"'",
        )
        for token in question.casefold().split()
    }

    return bool(
        tokens.intersection(
            REFERENCE_PRONOUNS,
        )
    )


def _contains_contextual_phrase(
    question: str,
) -> bool:
    """
    Detect generic conversational phrases
    that commonly depend on previous turns.

    This function is intentionally domain-agnostic.
    """

    normalized = question.casefold().strip()

    return any(phrase in normalized for phrase in CONTEXTUAL_PHRASES)


def _is_obviously_standalone(
    question: str,
) -> bool:
    """
    Determine whether a question can safely
    bypass the LLM rewriter.

    This is intentionally conservative.

    Only questions that contain no obvious
    conversational dependency are treated as
    standalone.
    """

    normalized = question.casefold().strip()

    if not normalized:
        return False

    if _contains_reference_pronoun(
        normalized,
    ):
        return False

    return not _contains_contextual_phrase(normalized)


def rewrite_question(
    question: str,
    messages: list[ConversationMessage],
) -> RewriteResult:
    """
    Resolve and rewrite a conversational
    question into a standalone retrieval
    question.

    Standalone questions use a fast path.

    Potentially contextual questions are sent
    to the LLM with conversation history.

    Args:
        question:
            The user's current question.

        messages:
            Recent conversation history.

    Returns:
        RewriteResult containing:

        - question:
            Standalone retrieval question.

        - resolved:
            Whether sufficient context exists.
    """

    question = question.strip()

    if not question:
        return RewriteResult(
            question=question,
            resolved=False,
        )

    # --------------------------------------------------
    # Fast path
    # --------------------------------------------------

    if _is_obviously_standalone(
        question,
    ):
        return RewriteResult(
            question=question,
            resolved=True,
        )

    # --------------------------------------------------
    # Context-aware rewriting
    # --------------------------------------------------

    history = build_conversation_history(
        messages,
    )

    output = rewrite_chain.invoke(
        {
            "history": history,
            "question": question,
        }
    )

    result = _parse_rewrite_result(
        output,
        question,
    )

    return result
