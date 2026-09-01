from pathlib import Path

import pymupdf


class RawPDFExtractor:
    """Extract raw layout information from a PDF."""

    def __init__(self, pdf_path: str | Path):
        self.pdf_path = Path(pdf_path)

    def extract(self) -> list[dict]:
        """
        Extract pages, blocks, lines, and spans
        with layout and font metadata.
        """

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

                pages.append(page_data)

            return pages

        finally:
            document.close()

    def _extract_page(
        self,
        page: pymupdf.Page,
        page_number: int,
    ) -> dict:
        """Extract layout information from one page."""

        page_dict = page.get_text("dict")

        blocks = []

        for block_index, block in enumerate(page_dict["blocks"]):
            # Image blocks and other non-text blocks may not
            # contain a "lines" field.
            if "lines" not in block:
                continue

            block_data = {
                "block_index": block_index,
                "bbox": block.get("bbox"),
                "lines": [],
            }

            for line_index, line in enumerate(block["lines"]):
                line_data = {
                    "line_index": line_index,
                    "bbox": line.get("bbox"),
                    "spans": [],
                }

                for span_index, span in enumerate(line["spans"]):
                    span_data = {
                        "span_index": span_index,
                        "text": span.get("text", ""),
                        "bbox": span.get("bbox"),
                        "font": span.get("font"),
                        "font_size": span.get("size"),
                        "flags": span.get("flags"),
                    }

                    line_data["spans"].append(span_data)

                block_data["lines"].append(line_data)

            blocks.append(block_data)

        return {
            "page_number": page_number,
            "width": page.rect.width,
            "height": page.rect.height,
            "blocks": blocks,
        }