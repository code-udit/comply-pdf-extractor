from dataclasses import dataclass, field
from pathlib import Path


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
        return "".join(span.text for span in self.spans)


@dataclass
class Block:
    """A PDF text block containing one or more lines."""

    raw_index: int
    bbox: tuple[float, float, float, float]
    lines: list[Line] = field(default_factory=list)

    @property
    def text(self) -> str:
        return "\n".join(
            line.text
            for line in self.lines
            if line.text.strip()
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
    """A single PDF page."""

    page_number: int
    width: float
    height: float
    blocks: list[Block] = field(default_factory=list)

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