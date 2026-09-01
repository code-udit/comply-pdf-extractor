from pathlib import Path

from app.extraction.raw_extractor import RawPDFExtractor


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PDF_PATH = (
    PROJECT_ROOT
    / "sample_documents"
    / "AMGN-135003565.pdf"
)


def get_bold_status(flags: int | None) -> bool:
    """Return whether the PyMuPDF flags indicate bold."""

    if flags is None:
        return False

    return bool(flags & 16)


def print_block(block, display_index: int):
    print("\n" + "-" * 80)
    print(f"VISUAL BLOCK {display_index}")
    print(f"RAW BLOCK INDEX {block.raw_index}")
    print("-" * 80)

    print(f"bbox={block.bbox}")
    print(f"x0={block.x0}")
    print(f"y0={block.y0}")
    print(f"raw_text={block.text!r}")
    print(f"normalized_text={block.normalized_text!r}")

    for line in block.lines:
        print(f"\n  LINE {line.index}")
        print(f"  bbox={line.bbox}")
        print(f"  raw_text={line.text!r}")
        print(f"  normalized_text={line.normalized_text!r}")

        for span in line.spans:
            print("\n    SPAN")
            print(f"    raw_text={span.text!r}")
            print(f"    normalized_text={span.normalized_text!r}")
            print(f"    bbox={span.bbox}")
            print(f"    font={span.font!r}")
            print(f"    font_size={span.font_size}")
            print(f"    flags={span.flags}")
            print(f"    bold={get_bold_status(span.flags)}")


def main():
    print("=" * 80)
    print("RAW PDF DATA MODEL + VISUAL ORDER TEST")
    print("=" * 80)

    print(f"PDF: {PDF_PATH}")
    print(f"Exists: {PDF_PATH.exists()}")

    extractor = RawPDFExtractor(PDF_PATH)

    document = extractor.extract()

    print(f"Pages extracted: {document.page_count}")

    page = document.pages[0]

    print("\n" + "=" * 80)
    print(f"PAGE {page.page_number}")
    print("=" * 80)

    print(f"Page width:  {page.width}")
    print(f"Page height: {page.height}")
    print(f"Raw blocks:  {len(page.blocks)}")

    print("\n" + "=" * 80)
    print("VISUAL BLOCK ORDER")
    print("=" * 80)

    for display_index, block in enumerate(
        page.visual_blocks,
        start=1,
    ):
        print_block(
            block=block,
            display_index=display_index,
        )

    print("\n" + "=" * 80)
    print("RAW → VISUAL ORDER COMPARISON")
    print("=" * 80)

    for visual_index, block in enumerate(
        page.visual_blocks,
        start=1,
    ):
        print(
            f"Visual {visual_index:02d} "
            f"<- Raw {block.raw_index:02d} "
            f"| y={block.y0:7.2f} "
            f"| x={block.x0:7.2f} "
            f"| {block.text[:80]!r}"
        )

    print("\n" + "=" * 80)
    print("STEP 4 TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()