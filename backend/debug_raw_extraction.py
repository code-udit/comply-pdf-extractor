from pathlib import Path

from app.extraction.raw_extractor import RawPDFExtractor


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PDF_PATH = (
    PROJECT_ROOT
    / "sample_documents"
    / "AMGN-135003565.pdf"
)


def get_bold_status(flags: int | None) -> bool:
    """
    Determine whether the PyMuPDF font flags indicate bold.

    This is only a preliminary indicator.
    We will improve style classification later.
    """

    if flags is None:
        return False

    # PyMuPDF uses bit 4 for bold.
    return bool(flags & 16)


def main():
    print("=" * 80)
    print("RAW PDF LAYOUT EXTRACTION")
    print("=" * 80)

    print(f"PDF: {PDF_PATH}")
    print(f"Exists: {PDF_PATH.exists()}")

    extractor = RawPDFExtractor(PDF_PATH)

    pages = extractor.extract()

    print(f"Pages extracted: {len(pages)}")

    # For the first run, inspect only Page 1.
    page = pages[0]

    print("\n")
    print("=" * 80)
    print(f"PAGE {page['page_number']}")
    print("=" * 80)

    print(f"Page width:  {page['width']}")
    print(f"Page height: {page['height']}")
    print(f"Blocks:      {len(page['blocks'])}")

    for block in page["blocks"]:
        print("\n" + "-" * 80)
        print(f"BLOCK {block['block_index']}")
        print("-" * 80)

        print(f"bbox={block['bbox']}")
        print(f"lines={len(block['lines'])}")

        for line in block["lines"]:
            print(f"\n  LINE {line['line_index']}")
            print(f"  bbox={line['bbox']}")

            for span in line["spans"]:
                bold = get_bold_status(span["flags"])

                print("\n    SPAN")
                print(f"    text={span['text']!r}")
                print(f"    bbox={span['bbox']}")
                print(f"    font={span['font']!r}")
                print(f"    font_size={span['font_size']}")
                print(f"    flags={span['flags']}")
                print(f"    bold={bold}")

    print("\n")
    print("=" * 80)
    print("RAW EXTRACTION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()