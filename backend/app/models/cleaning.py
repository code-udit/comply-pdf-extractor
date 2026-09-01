from dataclasses import dataclass, field
from app.models.layout import LayoutSignals


@dataclass
class CleanBlock:
    """
    Cleaned representation of a raw PDF block.

    Keeps the original raw block separate from the cleaned text.
    """

    page_number: int
    raw_index: int
    text: str

    source_text: str = ""

    layout: LayoutSignals = field(
        default_factory=LayoutSignals
    )

    removed_as_noise: bool = False
    removal_reason: str | None = None


@dataclass
class CleanPage:
    """
    Cleaned representation of one PDF page.
    """

    page_number: int
    blocks: list[CleanBlock] = field(
        default_factory=list
    )


@dataclass
class CleanDocument:
    """
    Cleaned intermediate representation of a PDF document.
    """

    pages: list[CleanPage] = field(
        default_factory=list
    )