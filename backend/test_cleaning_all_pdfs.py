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
    print("CLEANING SERVICE - ALL PDF TEST")
    print("=" * 80)

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

        clean_result = clean_document(document)

        raw_blocks = sum(
            len(page.blocks)
            for page in document.pages
        )

        clean_blocks = sum(
            len(page.blocks)
            for page in clean_result.pages
        )

        removed_blocks = raw_blocks - clean_blocks

        print(f"Pages:         {document.page_count}")
        print(f"Raw blocks:    {raw_blocks}")
        print(f"Clean blocks:  {clean_blocks}")
        print(f"Removed:       {removed_blocks}")

        if clean_result.pages:
            print("Result: PASS")
        else:
            print("Result: FAIL")

    print()
    print("=" * 80)
    print("ALL PDF CLEANING TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()