"""Shared pytest fixtures for the backend test suite.

These fixtures build small PDFs in-memory with pymupdf so the suite
does not depend on real SERFF sample filings being present on disk
(sample_documents/ is gitignored and may be empty in CI or on a
fresh checkout).
"""
from pathlib import Path

import pymupdf
import pytest


@pytest.fixture
def simple_pdf(tmp_path: Path) -> Path:
    """A two-page PDF with plain body text, no header/footer noise."""

    pdf_path = tmp_path / "simple.pdf"
    doc = pymupdf.open()

    page1 = doc.new_page()
    page1.insert_text((72, 100), "Section 1: Overview")
    page1.insert_text((72, 130), "This is the first page of the document.")

    page2 = doc.new_page()
    page2.insert_text((72, 100), "Section 2: Details")
    page2.insert_text((72, 130), "This is the second page of the document.")

    doc.save(pdf_path)
    doc.close()
    return pdf_path


@pytest.fixture
def serff_style_pdf(tmp_path: Path) -> Path:
    """A one-page PDF with a SERFF-style header and pipeline footer.

    Header text is placed near the top of the page and footer text
    near the bottom, matching the y-position heuristics used by
    app.extraction.noise_detector.
    """

    pdf_path = tmp_path / "serff.pdf"
    doc = pymupdf.open()

    page = doc.new_page()
    page_height = page.rect.height

    # Header block, within the top 15% of the page.
    page.insert_text((72, page_height * 0.05), "SERFF Tracking #: ABCD-123456789")

    # Body text, safely in the middle of the page.
    page.insert_text((72, page_height * 0.5), "Rate filing summary for review.")

    # Footer block, within the bottom 10% of the page.
    page.insert_text(
        (72, page_height * 0.95),
        "PDF Pipeline for SERFF Tracking Number ABCD-123456789 Generated 01/01/2026",
    )

    doc.save(pdf_path)
    doc.close()
    return pdf_path
