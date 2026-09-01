from pathlib import Path
from collections import Counter

from app.extraction.raw_extractor import RawPDFExtractor
from app.extraction.noise_detector import classify_page_noise
from app.extraction.layout_analyzer import analyze_page_layout
from app.services.cleaning_service import clean_document
from app.semantic.processor import process_document


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PDF_FILES = [
    "AMGN-135003565.pdf",
    "UNAM-135051123.pdf",
    "NYLM-134614243.pdf",
]


def main():
    print("=" * 80)
    print("SEMANTIC VALIDATION")
    print("=" * 80)

    all_passed = True

    for filename in PDF_FILES:
        print()
        print(f"VALIDATING: {filename}")
        print("-" * 80)

        pdf_path = PROJECT_ROOT / "sample_documents" / filename

        extractor = RawPDFExtractor(pdf_path)
        document = extractor.extract()

        for page in document.pages:
            classify_page_noise(page)
            analyze_page_layout(page)

        cleaned_document = clean_document(document)
        semantic_blocks = process_document(cleaned_document)

        type_counts = Counter(
            block.semantic_type.value
            for block in semantic_blocks
        )

        expected_pages = document.page_count
        actual_pages = len(cleaned_document.pages)

        valid_page_count = (
            expected_pages == actual_pages
        )

        valid_blocks = all(
            block.page_number >= 1
            and block.source_block_index >= 0
            and 0.0 <= block.confidence <= 1.0
            for block in semantic_blocks
        )

        has_semantic_blocks = len(semantic_blocks) > 0

        print(f"Pages:             {actual_pages}")
        print(f"Semantic blocks:   {len(semantic_blocks)}")
        print(f"Semantic types:    {dict(type_counts)}")

        print()
        print(f"Page count valid:  {valid_page_count}")
        print(f"Blocks valid:      {valid_blocks}")
        print(f"Blocks present:    {has_semantic_blocks}")

        passed = (
            valid_page_count
            and valid_blocks
            and has_semantic_blocks
        )

        if passed:
            print("RESULT: PASS")
        else:
            print("RESULT: FAIL")
            all_passed = False

    print()
    print("=" * 80)

    if all_passed:
        print("SEMANTIC VALIDATION PASSED")
    else:
        print("SEMANTIC VALIDATION FAILED")

    print("=" * 80)


if __name__ == "__main__":
    main()