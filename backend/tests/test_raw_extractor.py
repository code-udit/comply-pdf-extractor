from pathlib import Path

import pytest

from app.extraction.raw_extractor import RawPDFExtractor


def test_extract_returns_one_page_per_pdf_page(simple_pdf: Path):
    document = RawPDFExtractor(simple_pdf).extract()
    assert len(document.pages) == 2


def test_extracted_page_has_blocks_with_text(simple_pdf: Path):
    document = RawPDFExtractor(simple_pdf).extract()
    first_page = document.pages[0]

    assert len(first_page.blocks) > 0

    all_text = " ".join(
        span.text
        for block in first_page.blocks
        for line in block.lines
        for span in line.spans
    )
    assert "Overview" in all_text


def test_page_dimensions_are_populated(simple_pdf: Path):
    document = RawPDFExtractor(simple_pdf).extract()
    first_page = document.pages[0]

    assert first_page.width > 0
    assert first_page.height > 0


def test_missing_file_raises_file_not_found(tmp_path: Path):
    extractor = RawPDFExtractor(tmp_path / "missing.pdf")
    with pytest.raises(FileNotFoundError):
        extractor.extract()


def test_non_pdf_extension_raises_value_error(tmp_path: Path):
    fake_file = tmp_path / "not_a_pdf.docx"
    fake_file.write_text("hello")

    extractor = RawPDFExtractor(fake_file)
    with pytest.raises(ValueError):
        extractor.extract()
