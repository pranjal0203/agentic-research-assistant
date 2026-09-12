from dataclasses import dataclass


@dataclass(slots=True)
class Citation:
    """
    Represents a source citation associated
    with a generated response.
    """

    title: str
    location: str
    url: str | None = None
