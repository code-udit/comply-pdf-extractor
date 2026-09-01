from pathlib import Path

from app.extraction.raw_extractor import RawPDFExtractor
from app.extraction.noise_detector import classify_page_noise
from app.extraction.layout_analyzer import analyze_page_layout
from app.semantic.classifier import classify_block


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PDF_PATH = (
    PROJECT_ROOT
    / "sample_documents"
    / "AMGN-135003565.pdf"
)


def main():
    print("=" * 60)
    print("SEMANTIC CLASSIFIER - REAL PDF TEST")
    print("=" * 60)

    extractor = RawPDFExtractor(PDF_PATH)

    document = extractor.extract()

    page = document.pages[0]

    classify_page_noise(page)
    analyze_page_layout(page)

    print()
    print("PAGE 1 SEMANTIC BLOCKS")
    print("-" * 60)

    classified = []

    for block in page.visual_blocks:
        if block.noise_type.value != "none":
            continue

        result = classify_block(
            block=block,
            page_number=page.page_number,
        )

        classified.append(result)

        print(
            f"Raw {block.raw_index:02d}"
            f" | type={result.semantic_type.value}"
            f" | confidence={result.confidence}"
            f" | text={result.text[:80]!r}"
        )

    assert classified
    assert all(
        result.page_number == 1
        for result in classified
    )

    print()
    print("=" * 60)
    print("REAL PDF SEMANTIC TEST PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()