from pathlib import Path

from app.extraction.raw_extractor import RawPDFExtractor
from app.extraction.noise_detector import classify_page_noise
from app.extraction.layout_analyzer import analyze_page_layout
from app.services.cleaning_service import clean_document
from app.semantic.processor import process_document
from app.semantic.grouping import group_semantic_blocks


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PDF_FILES = [
    "AMGN-135003565.pdf",
    "UNAM-135051123.pdf",
    "NYLM-134614243.pdf",
]


def count_descendant_blocks(section):
    total = len(section.blocks)

    for child in section.children:
        total += count_descendant_blocks(child)

    return total


def main():
    print("=" * 80)
    print("HEADING / BODY GROUPING EVALUATION")
    print("=" * 80)

    all_passed = True

    for filename in PDF_FILES:
        print()
        print("=" * 80)
        print(f"EVALUATING: {filename}")
        print("=" * 80)

        pdf_path = PROJECT_ROOT / "sample_documents" / filename

        extractor = RawPDFExtractor(pdf_path)
        document = extractor.extract()

        for page in document.pages:
            classify_page_noise(page)
            analyze_page_layout(page)

        cleaned_document = clean_document(document)
        semantic_blocks = process_document(cleaned_document)
        sections = group_semantic_blocks(semantic_blocks)

        heading_count = sum(
            1
            for block in semantic_blocks
            if block.semantic_type.value == "heading"
        )

        grouped_block_count = sum(
            count_descendant_blocks(section)
            for section in sections
        )

        section_count = len(sections)

        print(f"Semantic blocks:       {len(semantic_blocks)}")
        print(f"Detected headings:     {heading_count}")
        print(f"Top-level sections:    {section_count}")
        print(f"Grouped blocks:        {grouped_block_count}")

        headings_grouped = (
            heading_count
            == sum(
                1
                for block in semantic_blocks
                if block.semantic_type.value == "heading"
            )
        )

        blocks_preserved = (
            grouped_block_count == len(semantic_blocks)
        )

        sections_present = section_count > 0

        print()
        print(f"Headings accounted for: {headings_grouped}")
        print(f"Blocks preserved:       {blocks_preserved}")
        print(f"Sections present:       {sections_present}")

        passed = (
            headings_grouped
            and blocks_preserved
            and sections_present
        )

        if passed:
            print("RESULT: PASS")
        else:
            print("RESULT: FAIL")
            all_passed = False

    print()
    print("=" * 80)

    if all_passed:
        print("HEADING / BODY GROUPING EVALUATION PASSED")
    else:
        print("HEADING / BODY GROUPING EVALUATION FAILED")

    print("=" * 80)


if __name__ == "__main__":
    main()