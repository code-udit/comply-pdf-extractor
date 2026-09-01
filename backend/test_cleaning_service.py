from pathlib import Path

from app.extraction.raw_extractor import RawPDFExtractor
from app.extraction.noise_detector import classify_page_noise
from app.services.cleaning_service import clean_document


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PDF_PATH = (
    PROJECT_ROOT
    / "sample_documents"
    / "AMGN-135003565.pdf"
)


def main():
    print("=" * 80)
    print("CLEANING SERVICE TEST")
    print("=" * 80)

    extractor = RawPDFExtractor(PDF_PATH)

    document = extractor.extract()

    # Classify noise before cleaning.
    for page in document.pages:
        classify_page_noise(page)

    clean_document_result = clean_document(document)

    print()
    print("CLEANING SUMMARY")
    print("-" * 80)

    raw_blocks = sum(
        len(page.blocks)
        for page in document.pages
    )

    clean_blocks = sum(
        len(page.blocks)
        for page in clean_document_result.pages
    )

    print(f"Raw blocks:   {raw_blocks}")
    print(f"Clean blocks: {clean_blocks}")
    print(f"Removed:      {raw_blocks - clean_blocks}")

    print()
    print("PAGE 1 CLEAN BLOCKS")
    print("-" * 80)

    page = clean_document_result.pages[0]

    for block in page.blocks:
        print(
            f"Raw {block.raw_index:02d}"
            f" | text={block.text!r}"
        )

    print()
    print("=" * 80)
    print("CLEANING SERVICE TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()