from pathlib import Path

from app.extraction.raw_extractor import RawPDFExtractor
from app.extraction.noise_detector import classify_page_noise
from app.extraction.layout_analyzer import analyze_page_layout
from app.extraction.page_layout_analyzer import analyze_page_layout_summary
from app.services.cleaning_service import clean_document


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PDF_FILES = [
    "AMGN-135003565.pdf",
    "UNAM-135051123.pdf",
    "NYLM-134614243.pdf",
]


def main():
    print("=" * 80)
    print("STAGE 5 END-TO-END PIPELINE TEST")
    print("=" * 80)

    all_passed = True

    for filename in PDF_FILES:
        print()
        print("=" * 80)
        print(f"PROCESSING: {filename}")
        print("=" * 80)

        pdf_path = PROJECT_ROOT / "sample_documents" / filename

        # 1. Raw extraction
        extractor = RawPDFExtractor(pdf_path)
        document = extractor.extract()

        raw_pages = document.page_count
        raw_blocks = sum(
            len(page.blocks)
            for page in document.pages
        )

        # 2. Noise analysis + layout analysis
        for page in document.pages:
            classify_page_noise(page)
            analyze_page_layout(page)
            analyze_page_layout_summary(page)

        # 3. Cleaning
        clean_result = clean_document(document)

        clean_pages = len(clean_result.pages)
        clean_blocks = sum(
            len(page.blocks)
            for page in clean_result.pages
        )

        removed_blocks = raw_blocks - clean_blocks

        passed = (
            raw_pages == clean_pages
            and clean_blocks > 0
            and removed_blocks >= 0
        )

        print(f"Raw pages:       {raw_pages}")
        print(f"Clean pages:     {clean_pages}")
        print(f"Raw blocks:      {raw_blocks}")
        print(f"Clean blocks:    {clean_blocks}")
        print(f"Removed blocks:  {removed_blocks}")

        if passed:
            print("RESULT: PASS")
        else:
            print("RESULT: FAIL")
            all_passed = False

    print()
    print("=" * 80)

    if all_passed:
        print("STAGE 5 END-TO-END TEST PASSED")
    else:
        print("STAGE 5 END-TO-END TEST FAILED")

    print("=" * 80)


if __name__ == "__main__":
    main()












