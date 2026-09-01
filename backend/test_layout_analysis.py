from pathlib import Path

from app.extraction.layout_analyzer import analyze_page_layout
from app.extraction.noise_detector import classify_page_noise
from app.extraction.raw_extractor import RawPDFExtractor


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PDF_FILES = [
    "AMGN-135003565.pdf",
    "UNAM-135051123.pdf",
    "NYLM-134614243.pdf",
]


def main():
    print("=" * 80)
    print("LAYOUT ANALYSIS - ALL PDF TEST")
    print("=" * 80)

    for filename in PDF_FILES:

        pdf_path = PROJECT_ROOT / "sample_documents" / filename

        print()
        print("=" * 80)
        print(f"PROCESSING: {filename}")
        print("=" * 80)

        extractor = RawPDFExtractor(pdf_path)
        document = extractor.extract()

        print(f"Pages: {len(document.pages)}")

        total_blocks = 0
        total_layout_blocks = 0

        for page in document.pages:

            classify_page_noise(page)
            analyze_page_layout(page)

            total_blocks += len(page.visual_blocks)

            for block in page.visual_blocks:
                if block.layout is not None:
                    total_layout_blocks += 1

        print(f"Visual blocks: {total_blocks}")
        print(f"Layout blocks: {total_layout_blocks}")

        if total_blocks == total_layout_blocks:
            print("RESULT: PASS")
        else:
            print("RESULT: FAIL")

    print()
    print("=" * 80)
    print("ALL PDF LAYOUT TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()