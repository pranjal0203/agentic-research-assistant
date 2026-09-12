"""
Application configuration.

This module contains all configurable
constants used throughout the application.
"""

from pathlib import Path

# -----------------------------
# Documents
# -----------------------------

DATA_DIR: Path = Path("data")

SUPPORTED_DOCUMENT_TYPES: tuple[str, ...] = (".pdf",)


# -----------------------------
# Vector Database
# -----------------------------

CHROMA_DB_PATH: Path = Path("db")


# -----------------------------
# Retrieval
# -----------------------------

# Number of candidates ultimately expected
# to survive retrieval/reranking.
TOP_K = 12

# Retrieve a broader candidate pool before
# downstream reranking.
#
# Example:
#   TOP_K = 12
#   multiplier = 3
#   retrieval candidates = 36
#
# This is intentionally domain-agnostic.
RETRIEVAL_CANDIDATE_MULTIPLIER = 3

CHUNK_SIZE = 1200

CHUNK_OVERLAP = 250

# Maximum number of retrieved candidates exposed
# to the follow-up planner.
FOLLOW_UP_OBSERVATION_TOP_K = 3

# Maximum characters retained from each candidate
# when building follow-up planner observations.
FOLLOW_UP_OBSERVATION_MAX_CHARS = 800

# Maximum number of candidates exposed to the
# final answer generator.
GENERATION_CONTEXT_TOP_K = 5

# Maximum characters retained from an individual
# candidate in the final generation context.
GENERATION_CONTEXT_MAX_CHARS = 2500

# -----------------------------
# Embeddings
# -----------------------------

EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"


# -----------------------------
# LLM
# -----------------------------

# Fast, higher-quota model used during
# v3 stabilization.
MODEL_NAME = "openai/gpt-oss-120b"

# TEMPERATURE = 0
TEMPERATURE = 0


# -----------------------------
# Web Search
# -----------------------------

TAVILY_MAX_RESULTS = 5


# -----------------------------
# Retrieval Evaluation
# -----------------------------

PDF_RETRIEVAL_THRESHOLD = 1.25

WEB_RETRIEVAL_THRESHOLD = 0.50

# Confidence evaluation thresholds
PDF_CONFIDENCE_VERY_HIGH = 0.90
PDF_CONFIDENCE_HIGH = 1.05

WEB_CONFIDENCE_VERY_HIGH = 0.90
WEB_CONFIDENCE_HIGH = 0.75


# -----------------------------
# Cross-source Reranking
# -----------------------------

HYBRID_TOP_K = 8

MIN_SOURCE_RELEVANCE = 0.40


# -----------------------------
# Conversation Memory
# -----------------------------

MAX_CONVERSATION_MESSAGES = 10


# -----------------------------
# Index Management
# -----------------------------

INDEX_MANIFEST_FILENAME = "manifest.json"


# -----------------------------
# Agent Max Iterations / Executions
# -----------------------------

MAX_AGENT_ITERATIONS = 3

MAX_TOOL_EXECUTIONS_PER_RUN = 2


# -----------------------------
# AI Gateway (OmniRoute)
# -----------------------------

USE_OMNIROUTE: bool = True

OMNIROUTE_API_BASE = "http://localhost:20128/v1"
