from pathlib import Path

from app.extraction.noise_detector import classify_page_noise
from app.extraction.raw_extractor import RawPDFExtractor
from app.models.document import NoiseType


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PDF_PATH = (
    PROJECT_ROOT
    / "sample_documents"
    / "AMGN-135003565.pdf"
)


def main():
    print("=" * 80)
    print("NOISE DETECTION TEST")
    print("=" * 80)

    extractor = RawPDFExtractor(PDF_PATH)

    document = extractor.extract()

    page = document.pages[0]

    classify_page_noise(page)

    print()
    print("PAGE 1 CLASSIFICATIONS")
    print("-" * 80)

    for block in page.visual_blocks:
        print(
            f"Raw {block.raw_index:02d} "
            f"| y={block.y0:8.2f} "
            f"| type={block.noise_type.value:7} "
            f"| {block.text[:100]!r}"
        )

    headers = [
        block
        for block in page.blocks
        if block.noise_type == NoiseType.HEADER
    ]

    footers = [
        block
        for block in page.blocks
        if block.noise_type == NoiseType.FOOTER
    ]

    print()
    print("SUMMARY")
    print("-" * 80)
    print(f"Headers detected: {len(headers)}")
    print(f"Footers detected: {len(footers)}")

    assert len(headers) >= 1
    assert len(footers) == 1

    print()
    print("=" * 80)
    print("NOISE DETECTION TEST PASSED")
    print("=" * 80)


if __name__ == "__main__":
    main()