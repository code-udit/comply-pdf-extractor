from pathlib import Path

from app.extraction.raw_extractor import RawPDFExtractor
from app.extraction.noise_detector import classify_page_noise
from app.services.cleaning_service import clean_document


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PDF_FILES = [
    "AMGN-135003565.pdf",
    "UNAM-135051123.pdf",
    "NYLM-134614243.pdf",
]


def main():
    print("=" * 80)
    print("CLEANING VALIDATION")
    print("=" * 80)

    all_passed = True

    for filename in PDF_FILES:
        print()
        print(f"VALIDATING: {filename}")
        print("-" * 80)

        pdf_path = PROJECT_ROOT / "sample_documents" / filename

        extractor = RawPDFExtractor(pdf_path)
        document = extractor.extract()

        raw_block_counts = [
            len(page.blocks)
            for page in document.pages
        ]

        for page in document.pages:
            classify_page_noise(page)

        expected_removed = sum(
            1
            for page in document.pages
            for block in page.blocks
            if block.noise_type.value != "none"
        )

        clean_result = clean_document(document)

        clean_block_count = sum(
            len(page.blocks)
            for page in clean_result.pages
        )

        actual_removed = (
            sum(raw_block_counts)
            - clean_block_count
        )

        noise_remaining = sum(
            1
            for page in clean_result.pages
            for block in page.blocks
            if block.removed_as_noise
        )

        raw_unchanged = all(
            len(page.blocks) == raw_block_counts[index]
            for index, page in enumerate(document.pages)
        )

        passed = (
            actual_removed == expected_removed
            and noise_remaining == 0
            and raw_unchanged
        )

        print(f"Expected removed: {expected_removed}")
        print(f"Actual removed:   {actual_removed}")
        print(f"Noise remaining:  {noise_remaining}")
        print(f"Raw unchanged:    {raw_unchanged}")

        if passed:
            print("RESULT: PASS")
        else:
            print("RESULT: FAIL")
            all_passed = False

    print()
    print("=" * 80)

    if all_passed:
        print("CLEANING VALIDATION PASSED")
    else:
        print("CLEANING VALIDATION FAILED")

    print("=" * 80)


if __name__ == "__main__":
    main()