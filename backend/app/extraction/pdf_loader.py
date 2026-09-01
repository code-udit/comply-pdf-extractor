from pathlib import Path

import pymupdf


class PDFLoader:
    """Load a PDF and provide basic page/text information."""

    def __init__(self, pdf_path: str | Path):
        self.pdf_path = Path(pdf_path)

    def load(self) -> pymupdf.Document:
        """Open and return the PDF document."""

        if not self.pdf_path.exists():
            raise FileNotFoundError(
                f"PDF file not found: {self.pdf_path}"
            )

        if self.pdf_path.suffix.lower() != ".pdf":
            raise ValueError(
                f"Expected a PDF file, got: {self.pdf_path.suffix}"
            )

        return pymupdf.open(self.pdf_path)

    def get_page_count(self) -> int:
        """Return the number of pages in the PDF."""

        document = self.load()

        try:
            return len(document)
        finally:
            document.close()

    def get_page_text(self, page_number: int) -> str:
        """Return plain text from a single page."""

        document = self.load()

        try:
            if page_number < 1 or page_number > len(document):
                raise ValueError(
                    f"Page number must be between 1 and {len(document)}"
                )

            page = document[page_number - 1]

            return page.get_text("text")
        finally:
            document.close()