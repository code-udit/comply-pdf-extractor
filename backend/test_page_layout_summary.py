from pathlib import Path

from app.extraction.layout_analyzer import analyze_page_layout
from app.extraction.noise_detector import classify_page_noise
from app.extraction.page_layout_analyzer import analyze_page_layout_summary
from app.extraction.raw_extractor import RawPDFExtractor


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PDF_PATH = (
    PROJECT_ROOT
    / "sample_documents"
    / "AMGN-135003565.pdf"
)


def main():
    print("=" * 80)
    print("PAGE LAYOUT SUMMARY TEST")
    print("=" * 80)

    extractor = RawPDFExtractor(PDF_PATH)

    document = extractor.extract()

    for page in document.pages:
        classify_page_noise(page)
        analyze_page_layout(page)
        analyze_page_layout_summary(page)

    print()
    print("PAGE SUMMARY TEST")
    print("-" * 80)

    for page in document.pages:
        summary = page.layout_summary

        print(
            f"Page {page.page_number:03d}"
            f" | blocks={summary.block_count}"
            f" | headers={summary.header_blocks}"
            f" | footers={summary.footer_blocks}"
            f" | lists={summary.list_like_blocks}"
            f" | tables={summary.table_like_blocks}"
        )

    print()
    print("=" * 80)
    print("PAGE LAYOUT SUMMARY TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()