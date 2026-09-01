from pathlib import Path

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
    print("STAGE 6 END-TO-END PIPELINE TEST")
    print("=" * 80)

    all_passed = True

    for filename in PDF_FILES:
        print()
        print("=" * 80)
        print(f"PROCESSING: {filename}")
        print("=" * 80)

        pdf_path = PROJECT_ROOT / "sample_documents" / filename

        # Stage 4: Raw extraction
        extractor = RawPDFExtractor(pdf_path)
        document = extractor.extract()

        # Stage 4: Noise + layout analysis
        for page in document.pages:
            classify_page_noise(page)
            analyze_page_layout(page)

        # Stage 5: Cleaning
        cleaned_document = clean_document(document)

        # Stage 6: Semantic processing
        semantic_blocks = process_document(
            cleaned_document
        )

        raw_pages = document.page_count
        clean_pages = len(cleaned_document.pages)
        clean_blocks = sum(
            len(page.blocks)
            for page in cleaned_document.pages
        )

        print(f"Raw pages:         {raw_pages}")
        print(f"Clean pages:       {clean_pages}")
        print(f"Clean blocks:      {clean_blocks}")
        print(f"Semantic blocks:   {len(semantic_blocks)}")

        passed = (
            raw_pages == clean_pages
            and clean_blocks == len(semantic_blocks)
            and len(semantic_blocks) > 0
        )

        if passed:
            print("RESULT: PASS")
        else:
            print("RESULT: FAIL")
            all_passed = False

    print()
    print("=" * 80)

    if all_passed:
        print("STAGE 6 END-TO-END TEST PASSED")
    else:
        print("STAGE 6 END-TO-END TEST FAILED")

    print("=" * 80)


if __name__ == "__main__":
    main()