from pathlib import Path

import pymupdf

from app.extraction.layout_analyzer import analyze_page_layout
from app.models.document import (
    Block,
    Line,
    Page,
    PDFDocument,
    Span,
)


class RawPDFExtractor:
    """Extract raw layout information from a PDF."""

    def __init__(self, pdf_path: str | Path):
        self.pdf_path = Path(pdf_path)

    def extract(self) -> PDFDocument:
        """Extract the complete raw document structure."""

        if not self.pdf_path.exists():
            raise FileNotFoundError(
                f"PDF file not found: {self.pdf_path}"
            )

        if self.pdf_path.suffix.lower() != ".pdf":
            raise ValueError(
                f"Expected a PDF file, got: {self.pdf_path.suffix}"
            )

        document = pymupdf.open(self.pdf_path)

        try:
            pages = []

            for page_index, page in enumerate(document):
                page_data = self._extract_page(
                    page=page,
                    page_number=page_index + 1,
                )

                analyze_page_layout(page_data)

                pages.append(page_data)

            return PDFDocument(
                source=self.pdf_path,
                pages=pages,
            )

        finally:
            document.close()

    def _extract_page(
        self,
        page: pymupdf.Page,
        page_number: int,
    ) -> Page:
        """Extract one PDF page into our internal model."""

        page_dict = page.get_text("dict")

        blocks = []

        for block_index, raw_block in enumerate(
            page_dict["blocks"]
        ):
            # Ignore non-text blocks for now.
            if "lines" not in raw_block:
                continue

            lines = []

            for line_index, raw_line in enumerate(
                raw_block["lines"]
            ):
                spans = []

                for span_index, raw_span in enumerate(
                    raw_line["spans"]
                ):
                    spans.append(
                        Span(
                            index=span_index,
                            text=raw_span.get("text", ""),
                            bbox=tuple(raw_span["bbox"]),
                            font=raw_span.get("font"),
                            font_size=raw_span.get("size"),
                            flags=raw_span.get("flags"),
                        )
                    )

                lines.append(
                    Line(
                        index=line_index,
                        bbox=tuple(raw_line["bbox"]),
                        spans=spans,
                    )
                )

            blocks.append(
                Block(
                    raw_index=block_index,
                    bbox=tuple(raw_block["bbox"]),
                    lines=lines,
                )
            )

        return Page(
            page_number=page_number,
            width=page.rect.width,
            height=page.rect.height,
            blocks=blocks,
        )