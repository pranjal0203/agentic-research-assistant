"""
Response source model.
"""

from enum import Enum


class Source(Enum):
    """
    Source used to generate a response.
    """

    PDF = "PDF"
    WEB = "Web"
    HYBRID = "Hybrid"
    NONE = "None"
