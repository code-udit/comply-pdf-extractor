from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional
import re
from app.models.layout import LayoutSignals
from app.models.page_layout import PageLayoutSummary

class NoiseType(str, Enum):
    """Known PDF noise categories."""

    NONE = "none"
    HEADER = "header"
    FOOTER = "footer"

def normalize_text(text: str) -> str:
    """
    Safely normalize extracted PDF text.

    The original text is never modified.
    """

    if not text:
        return ""

    # Replace tabs and line breaks with spaces.
    text = text.replace("\t", " ")
    text = text.replace("\r", " ")
    text = text.replace("\n", " ")

    # Collapse repeated whitespace.
    text = re.sub(r"\s+", " ", text)

    # Remove leading/trailing whitespace.
    return text.strip()

@dataclass
class Span:
    """Smallest text/style unit extracted from a PDF."""

    index: int
    text: str
    bbox: tuple[float, float, float, float]
    font: str | None
    font_size: float | None
    flags: int | None

    @property
    def normalized_text(self) -> str:
        """Return safely normalized span text."""

        return normalize_text(self.text)

    @property
    def x0(self) -> float:
        return self.bbox[0]

    @property
    def y0(self) -> float:
        return self.bbox[1]

    @property
    def x1(self) -> float:
        return self.bbox[2]

    @property
    def y1(self) -> float:
        return self.bbox[3]


@dataclass
class Line:
    """A visual line containing one or more spans."""

    index: int
    bbox: tuple[float, float, float, float]
    spans: list[Span] = field(default_factory=list)

    @property
    def text(self) -> str:
        return "".join(
            span.text
            for span in self.spans
        )

    @property
    def normalized_text(self) -> str:
        """Return normalized text for the complete line."""

        return normalize_text(
            "".join(
                span.normalized_text
                for span in self.spans
            )
        )

@dataclass
class Block:
    raw_index: int
    bbox: tuple[float, float, float, float]
    lines: list[Line] = field(default_factory=list)

    noise_type: NoiseType = NoiseType.NONE
    noise_reason: Optional[str] = None

    layout: LayoutSignals = field(
        default_factory=LayoutSignals
    )

    @property
    def text(self) -> str:
        return "\n".join(
            line.text
            for line in self.lines
            if line.text.strip()
        )

    @property
    def normalized_text(self) -> str:
        """Return normalized text for the complete block."""

        return "\n".join(
            line.normalized_text
            for line in self.lines
            if line.normalized_text
        )

    @property
    def x0(self) -> float:
        return self.bbox[0]

    @property
    def y0(self) -> float:
        return self.bbox[1]

    @property
    def x1(self) -> float:
        return self.bbox[2]

    @property
    def y1(self) -> float:
        return self.bbox[3]


@dataclass
class Page:
    page_number: int
    width: float
    height: float
    blocks: list[Block] = field(default_factory=list)

    layout_summary: PageLayoutSummary = field(
        default_factory=PageLayoutSummary
    )

    @property
    def visual_blocks(self) -> list[Block]:
        """
        Return blocks in approximate visual reading order.

        Blocks that are vertically close are treated as belonging
        to the same visual row. Within each row, blocks are ordered
        from left to right.
        """

        if not self.blocks:
            return []

        row_y_tolerance = 3.0

        sorted_blocks = sorted(
            self.blocks,
            key=lambda block: block.y0,
        )

        rows: list[list[Block]] = []

        for block in sorted_blocks:
            placed_in_row = False

            for row in rows:
                row_reference_y = min(
                    existing_block.y0
                    for existing_block in row
                )

                if abs(block.y0 - row_reference_y) <= row_y_tolerance:
                    row.append(block)
                    placed_in_row = True
                    break

            if not placed_in_row:
                rows.append([block])

        ordered_blocks: list[Block] = []

        for row in rows:
            row.sort(key=lambda block: block.x0)
            ordered_blocks.extend(row)

        return ordered_blocks


@dataclass
class PDFDocument:
    """Complete raw PDF representation."""

    source: Path
    pages: list[Page] = field(default_factory=list)

    @property
    def page_count(self) -> int:
        return len(self.pages)