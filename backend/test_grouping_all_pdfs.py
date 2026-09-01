from pathlib import Path

from app.extraction.raw_extractor import RawPDFExtractor
from app.extraction.noise_detector import classify_page_noise
from app.extraction.layout_analyzer import analyze_page_layout
from app.services.cleaning_service import clean_document
from app.semantic.processor import process_document
from app.semantic.grouping import group_semantic_blocks


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PDF_FILES = [
    "AMGN-135003565.pdf",
    "UNAM-135051123.pdf",
    "NYLM-134614243.pdf",
]


def count_nested_sections(sections):
    total = len(sections)

    for section in sections:
        total += count_nested_sections(section.children)

    return total


def main():
    print("=" * 80)
    print("BODY GROUPING - ALL PDF TEST")
    print("=" * 80)

    all_passed = True

    for filename in PDF_FILES:
        print()
        print("=" * 80)
        print(f"PROCESSING: {filename}")
        print("=" * 80)

        pdf_path = PROJECT_ROOT / "sample_documents" / filename

        extractor = RawPDFExtractor(pdf_path)
        document = extractor.extract()

        for page in document.pages:
            classify_page_noise(page)
            analyze_page_layout(page)

        cleaned_document = clean_document(document)
        semantic_blocks = process_document(cleaned_document)

        sections = group_semantic_blocks(
            semantic_blocks
        )

        section_count = count_nested_sections(sections)

        print(f"Pages:             {document.page_count}")
        print(f"Semantic blocks:   {len(semantic_blocks)}")
        print(f"Top-level sections:{len(sections)}")
        print(f"Total sections:    {section_count}")

        passed = (
            document.page_count == len(cleaned_document.pages)
            and len(semantic_blocks) > 0
            and section_count > 0
        )

        if passed:
            print("RESULT: PASS")
        else:
            print("RESULT: FAIL")
            all_passed = False

    print()
    print("=" * 80)

    if all_passed:
        print("ALL PDF GROUPING TEST PASSED")
    else:
        print("ALL PDF GROUPING TEST FAILED")

    print("=" * 80)


if __name__ == "__main__":
    main()