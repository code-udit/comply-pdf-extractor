from pathlib import Path

import pytest

from app.extraction.pdf_loader import PDFLoader


def test_get_page_count(simple_pdf: Path):
    loader = PDFLoader(simple_pdf)
    assert loader.get_page_count() == 2


def test_get_page_text_returns_expected_content(simple_pdf: Path):
    loader = PDFLoader(simple_pdf)
    text = loader.get_page_text(1)
    assert "Section 1: Overview" in text


def test_get_page_text_second_page(simple_pdf: Path):
    loader = PDFLoader(simple_pdf)
    text = loader.get_page_text(2)
    assert "Section 2: Details" in text
    assert "Section 1" not in text


def test_get_page_text_invalid_page_number_raises(simple_pdf: Path):
    loader = PDFLoader(simple_pdf)
    with pytest.raises(ValueError):
        loader.get_page_text(99)


def test_missing_file_raises_file_not_found(tmp_path: Path):
    loader = PDFLoader(tmp_path / "does_not_exist.pdf")
    with pytest.raises(FileNotFoundError):
        loader.load()


def test_non_pdf_extension_raises_value_error(tmp_path: Path):
    fake_file = tmp_path / "not_a_pdf.txt"
    fake_file.write_text("hello")

    loader = PDFLoader(fake_file)
    with pytest.raises(ValueError):
        loader.load()
