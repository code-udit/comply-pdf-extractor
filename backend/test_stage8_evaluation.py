from pathlib import Path

from app.extraction.raw_extractor import RawPDFExtractor
from app.extraction.noise_detector import classify_page_noise
from app.extraction.layout_analyzer import analyze_page_layout
from app.services.cleaning_service import clean_document
from app.semantic.processor import process_document
from app.semantic.grouping import group_semantic_blocks


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PDF_EXPECTATIONS = {
    "AMGN-135003565.pdf": {
        "pages": 15,
        "clean_blocks": 280,
    },
    "UNAM-135051123.pdf": {
        "pages": 17,
        "clean_blocks": 310,
    },
    "NYLM-134614243.pdf": {
        "pages": 114,
        "clean_blocks": 5273,
    },
}


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


def process_pdf(filename):
    pdf_path = PROJECT_ROOT / "sample_documents" / filename

    extractor = RawPDFExtractor(pdf_path)
    document = extractor.extract()

    for page in document.pages:
        classify_page_noise(page)
        analyze_page_layout(page)

    cleaned_document = clean_document(document)
    semantic_blocks = process_document(cleaned_document)
    sections = group_semantic_blocks(semantic_blocks)

    return (
        document,
        cleaned_document,
        semantic_blocks,
        sections,
    )


def main():
    print("=" * 80)
    print("STAGE 8 PDF EVALUATION")
    print("=" * 80)

    all_passed = True

    for filename, expected in PDF_EXPECTATIONS.items():
        print()
        print("=" * 80)
        print(f"EVALUATING: {filename}")
        print("=" * 80)

        (
            document,
            cleaned_document,
            semantic_blocks,
            sections,
        ) = process_pdf(filename)

        actual_pages = document.page_count
        clean_pages = len(cleaned_document.pages)
        clean_blocks = sum(
            len(page.blocks)
            for page in cleaned_document.pages
        )
        semantic_count = len(semantic_blocks)
        section_count = count_sections(sections)
        grouped_blocks = count_grouped_blocks(sections)

        page_check = actual_pages == expected["pages"]
        clean_page_check = clean_pages == expected["pages"]
        block_check = clean_blocks == expected["clean_blocks"]
        semantic_check = semantic_count == clean_blocks
        grouping_check = grouped_blocks == semantic_count
        section_check = section_count > 0

        print(f"Expected pages:       {expected['pages']}")
        print(f"Actual pages:         {actual_pages}")
        print(f"Clean pages:          {clean_pages}")
        print(f"Expected clean blocks:{expected['clean_blocks']}")
        print(f"Actual clean blocks:  {clean_blocks}")
        print(f"Semantic blocks:      {semantic_count}")
        print(f"Sections:             {section_count}")
        print(f"Grouped blocks:       {grouped_blocks}")

        print()
        print(f"Page count:           {page_check}")
        print(f"Clean pages:          {clean_page_check}")
        print(f"Clean block count:    {block_check}")
        print(f"Semantic count:       {semantic_check}")
        print(f"Grouping preserved:   {grouping_check}")
        print(f"Sections present:     {section_check}")

        passed = (
            page_check
            and clean_page_check
            and block_check
            and semantic_check
            and grouping_check
            and section_check
        )

        if passed:
            print("RESULT: PASS")
        else:
            print("RESULT: FAIL")
            all_passed = False

    print()
    print("=" * 80)

    if all_passed:
        print("STAGE 8 PDF EVALUATION PASSED")
    else:
        print("STAGE 8 PDF EVALUATION FAILED")

    print("=" * 80)


if __name__ == "__main__":
    main()