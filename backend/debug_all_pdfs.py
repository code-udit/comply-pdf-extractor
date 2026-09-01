from pathlib import Path

from app.extraction.raw_extractor import RawPDFExtractor


PROJECT_ROOT = Path(__file__).resolve().parent.parent

SAMPLE_DOCUMENTS = PROJECT_ROOT / "sample_documents"

DEBUG_OUTPUT = PROJECT_ROOT / "debug_output"


PDF_FILES = [
    "AMGN-135003565.pdf",
    "UNAM-135051123.pdf",
    "NYLM-134614243.pdf",
]


def get_bold_status(flags: int | None) -> bool:
    """Return whether PyMuPDF font flags indicate bold."""

    if flags is None:
        return False

    return bool(flags & 16)


def write_span(
    file,
    span,
):
    """Write one span to the debug file."""

    bold = get_bold_status(span.flags)

    file.write("        SPAN\n")
    file.write(f"        index={span.index}\n")
    file.write(f"        text={span.text!r}\n")
    file.write(f"        bbox={span.bbox}\n")
    file.write(f"        x0={span.x0}\n")
    file.write(f"        y0={span.y0}\n")
    file.write(f"        x1={span.x1}\n")
    file.write(f"        y1={span.y1}\n")
    file.write(f"        font={span.font!r}\n")
    file.write(f"        font_size={span.font_size}\n")
    file.write(f"        flags={span.flags}\n")
    file.write(f"        bold={bold}\n")
    file.write("\n")


def write_block(
    file,
    block,
    visual_index: int,
):
    """Write one block and its lines/spans."""

    file.write("\n")
    file.write("=" * 80 + "\n")
    file.write(f"VISUAL BLOCK {visual_index}\n")
    file.write("=" * 80 + "\n")

    file.write(f"raw_index={block.raw_index}\n")
    file.write(f"bbox={block.bbox}\n")
    file.write(f"x0={block.x0}\n")
    file.write(f"y0={block.y0}\n")
    file.write(f"x1={block.x1}\n")
    file.write(f"y1={block.y1}\n")
    file.write(f"text={block.text!r}\n")
    file.write(f"lines={len(block.lines)}\n")

    for line in block.lines:
        file.write("\n")
        file.write(f"    LINE {line.index}\n")
        file.write(f"    bbox={line.bbox}\n")
        file.write(f"    text={line.text!r}\n")
        file.write(f"    spans={len(line.spans)}\n")
        file.write("\n")

        for span in line.spans:
            write_span(file, span)


def write_page(
    file,
    page,
):
    """Write one complete page."""

    file.write("\n")
    file.write("#" * 80 + "\n")
    file.write(f"PAGE {page.page_number}\n")
    file.write("#" * 80 + "\n")

    file.write(f"width={page.width}\n")
    file.write(f"height={page.height}\n")
    file.write(f"raw_blocks={len(page.blocks)}\n")
    file.write(
        f"visual_blocks={len(page.visual_blocks)}\n"
    )

    file.write("\n")
    file.write("VISUAL BLOCK SUMMARY\n")
    file.write("-" * 80 + "\n")

    for visual_index, block in enumerate(
        page.visual_blocks,
        start=1,
    ):
        preview = block.text.replace("\n", " ")[:120]

        file.write(
            f"Visual {visual_index:03d} "
            f"| Raw {block.raw_index:03d} "
            f"| x={block.x0:8.2f} "
            f"| y={block.y0:8.2f} "
            f"| {preview!r}\n"
        )

    for visual_index, block in enumerate(
        page.visual_blocks,
        start=1,
    ):
        write_block(
            file=file,
            block=block,
            visual_index=visual_index,
        )


def process_pdf(pdf_name: str):
    """Extract and write one complete PDF."""

    pdf_path = SAMPLE_DOCUMENTS / pdf_name

    if not pdf_path.exists():
        print(f"[SKIP] {pdf_name} - file not found")
        return

    document_name = pdf_path.stem

    output_directory = DEBUG_OUTPUT / document_name

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    print()
    print("=" * 80)
    print(f"PROCESSING: {pdf_name}")
    print("=" * 80)

    extractor = RawPDFExtractor(pdf_path)

    document = extractor.extract()

    print(f"Pages: {document.page_count}")

    for page in document.pages:
        output_file = (
            output_directory
            / f"page_{page.page_number:03d}.txt"
        )

        with output_file.open(
            "w",
            encoding="utf-8",
        ) as file:

            file.write(
                f"PDF: {pdf_name}\n"
            )

            file.write(
                f"PAGE: {page.page_number}\n"
            )

            write_page(
                file=file,
                page=page,
            )

        print(
            f"  Page {page.page_number:03d} "
            f"-> {output_file.relative_to(PROJECT_ROOT)}"
        )

    print(
        f"[COMPLETE] {pdf_name}"
    )


def main():
    print("=" * 80)
    print("COMPLETE RAW PDF DEBUG EXTRACTION")
    print("=" * 80)

    DEBUG_OUTPUT.mkdir(
        parents=True,
        exist_ok=True,
    )

    for pdf_name in PDF_FILES:
        process_pdf(pdf_name)

    print()
    print("=" * 80)
    print("ALL PDF EXTRACTION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()