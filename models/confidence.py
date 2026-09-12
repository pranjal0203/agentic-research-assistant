"""
Confidence level model.
"""

from enum import Enum


class Confidence(Enum):
    """
    Retrieval confidence levels.
    """

    VERY_HIGH = "Very High"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    NONE = "None"
