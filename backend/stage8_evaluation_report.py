from pathlib import Path
from collections import Counter

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


def count_sections(sections):
    total = len(sections)

    for section in sections:
        total += count_sections(section.children)

    return total


def count_grouped_blocks(sections):
    total = 0

    for section in sections:
        total += len(section.blocks)
        total += count_grouped_blocks(section.children)

    return total


def main():
    print("=" * 80)
    print("STAGE 8 EVALUATION REPORT")
    print("=" * 80)

    for filename in PDF_FILES:
        pdf_path = PROJECT_ROOT / "sample_documents" / filename

        extractor = RawPDFExtractor(pdf_path)
        document = extractor.extract()

        for page in document.pages:
            classify_page_noise(page)
            analyze_page_layout(page)

        cleaned_document = clean_document(document)
        semantic_blocks = process_document(cleaned_document)
        sections = group_semantic_blocks(semantic_blocks)

        type_counts = Counter(
            block.semantic_type.value
            for block in semantic_blocks
        )

        heading_count = type_counts.get("heading", 0)
        grouped_blocks = count_grouped_blocks(sections)
        section_count = count_sections(sections)

        print()
        print("=" * 80)
        print(f"DOCUMENT: {filename}")
        print("=" * 80)

        print(f"Pages:               {document.page_count}")
        print(f"Clean blocks:        {sum(len(page.blocks) for page in cleaned_document.pages)}")
        print(f"Semantic blocks:     {len(semantic_blocks)}")
        print(f"Sections:            {section_count}")
        print(f"Headings detected:   {heading_count}")
        print(f"Grouped blocks:      {grouped_blocks}")

        print()
        print("SEMANTIC TYPES")
        print("-" * 80)

        for semantic_type, count in sorted(type_counts.items()):
            print(f"{semantic_type:20} {count}")

        print()
        print("INTEGRITY")
        print("-" * 80)
        print(
            f"Pages preserved:     "
            f"{document.page_count == len(cleaned_document.pages)}"
        )
        print(
            f"Blocks preserved:    "
            f"{grouped_blocks == len(semantic_blocks)}"
        )
        print(
            f"Sections present:    "
            f"{section_count > 0}"
        )

    print()
    print("=" * 80)
    print("STAGE 8 EVALUATION REPORT COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()