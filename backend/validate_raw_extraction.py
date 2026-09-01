from pathlib import Path

from app.extraction.raw_extractor import RawPDFExtractor


PROJECT_ROOT = Path(__file__).resolve().parent.parent

SAMPLE_DOCUMENTS = PROJECT_ROOT / "sample_documents"


PDF_FILES = [
    ("AMGN-135003565.pdf", 15),
    ("UNAM-135051123.pdf", 17),
    ("NYLM-134614243.pdf", 114),
]


def validate_bbox(bbox):
    """Validate a bounding box."""

    if bbox is None:
        return False, "bbox is None"

    if len(bbox) != 4:
        return False, "bbox does not contain 4 values"

    x0, y0, x1, y1 = bbox

    values = (x0, y0, x1, y1)

    if any(value is None for value in values):
        return False, "bbox contains None"

    if x1 < x0:
        return False, "x1 < x0"

    if y1 < y0:
        return False, "y1 < y0"

    return True, None


def validate_span(span, problems):
    """Validate one span."""

    valid, reason = validate_bbox(span.bbox)

    if not valid:
        problems.append(
            f"Invalid span bbox: {reason}"
        )

    if span.text is None:
        problems.append(
            "Span text is None"
        )

    if span.font is None:
        problems.append(
            f"Missing font metadata for span: {span.text!r}"
        )

    if span.font_size is None:
        problems.append(
            f"Missing font size for span: {span.text!r}"
        )


def validate_line(line, problems):
    """Validate one line."""

    valid, reason = validate_bbox(line.bbox)

    if not valid:
        problems.append(
            f"Invalid line bbox: {reason}"
        )

    if not line.spans:
        problems.append(
            f"Line {line.index} contains no spans"
        )

    for span in line.spans:
        validate_span(
            span=span,
            problems=problems,
        )


def validate_block(block, problems):
    """Validate one block."""

    valid, reason = validate_bbox(block.bbox)

    if not valid:
        problems.append(
            f"Invalid block bbox: {reason}"
        )

    if not block.lines:
        problems.append(
            f"Block {block.raw_index} contains no lines"
        )

    for line in block.lines:
        validate_line(
            line=line,
            problems=problems,
        )


def validate_page(page):
    """Validate one page and return statistics."""

    problems = []

    if page.width <= 0:
        problems.append(
            f"Invalid page width: {page.width}"
        )

    if page.height <= 0:
        problems.append(
            f"Invalid page height: {page.height}"
        )

    if not page.blocks:
        problems.append(
            "Page contains no text blocks"
        )

    block_count = len(page.blocks)
    line_count = 0
    span_count = 0
    text_characters = 0

    for block in page.blocks:
        validate_block(
            block=block,
            problems=problems,
        )

        line_count += len(block.lines)

        for line in block.lines:
            span_count += len(line.spans)

            for span in line.spans:
                text_characters += len(span.text)

    return {
        "page_number": page.page_number,
        "blocks": block_count,
        "lines": line_count,
        "spans": span_count,
        "characters": text_characters,
        "problems": problems,
    }


def validate_pdf(
    pdf_name: str,
    expected_pages: int,
):
    """Validate an entire PDF."""

    pdf_path = SAMPLE_DOCUMENTS / pdf_name

    print()
    print("=" * 80)
    print(f"VALIDATING: {pdf_name}")
    print("=" * 80)

    if not pdf_path.exists():
        print("[FAIL] PDF file not found")
        return False

    extractor = RawPDFExtractor(pdf_path)

    document = extractor.extract()

    actual_pages = document.page_count

    print(f"Expected pages: {expected_pages}")
    print(f"Actual pages:   {actual_pages}")

    if actual_pages != expected_pages:
        print("[FAIL] Page count mismatch")
        return False

    total_blocks = 0
    total_lines = 0
    total_spans = 0
    total_characters = 0

    problematic_pages = []

    for page in document.pages:
        result = validate_page(page)

        total_blocks += result["blocks"]
        total_lines += result["lines"]
        total_spans += result["spans"]
        total_characters += result["characters"]

        if result["problems"]:
            problematic_pages.append(result)

    print()
    print("DOCUMENT TOTALS")
    print("-" * 80)
    print(f"Pages:      {actual_pages}")
    print(f"Blocks:     {total_blocks}")
    print(f"Lines:      {total_lines}")
    print(f"Spans:      {total_spans}")
    print(f"Characters: {total_characters}")

    print()
    print("VALIDATION")
    print("-" * 80)

    if problematic_pages:
        print(
            f"[WARNING] "
            f"{len(problematic_pages)} page(s) "
            f"have validation findings"
        )

        for page_result in problematic_pages:
            print()
            print(
                f"PAGE {page_result['page_number']}"
            )

            for problem in page_result["problems"]:
                print(f"  - {problem}")

        return False

    print("[PASS] No structural validation problems found")

    return True


def main():
    print("=" * 80)
    print("RAW PDF EXTRACTION VALIDATION")
    print("=" * 80)

    results = []

    for pdf_name, expected_pages in PDF_FILES:
        passed = validate_pdf(
            pdf_name=pdf_name,
            expected_pages=expected_pages,
        )

        results.append(
            (pdf_name, passed)
        )

    print()
    print("=" * 80)
    print("FINAL VALIDATION SUMMARY")
    print("=" * 80)

    all_passed = True

    for pdf_name, passed in results:
        status = "PASS" if passed else "FAIL"

        print(
            f"{status:>4} | {pdf_name}"
        )

        if not passed:
            all_passed = False

    print()

    if all_passed:
        print(
            "ALL PDFS PASSED RAW EXTRACTION VALIDATION"
        )
    else:
        print(
            "ONE OR MORE PDFS HAVE VALIDATION FINDINGS"
        )


if __name__ == "__main__":
    main()