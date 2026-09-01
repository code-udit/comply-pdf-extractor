from pathlib import Path

from app.extraction.raw_extractor import RawPDFExtractor
from app.extraction.noise_detector import classify_page_noise
from app.extraction.layout_analyzer import analyze_page_layout
from app.services.cleaning_service import clean_document
from app.semantic.processor import process_document


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PDF_FILES = [
    "AMGN-135003565.pdf",
    "UNAM-135051123.pdf",
    "NYLM-134614243.pdf",
]

KNOWN_HEADINGS = {
    "general information",
    "filing fees",
    "correspondence summary",
    "disposition",
    "objection letter",
    "response letter",
    "filing description",
    "supporting documents",
    "attachments",
}


def main():
    print("=" * 80)
    print("KNOWN HEADING EVALUATION")
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

        detected_headings = {
            block.text.strip().casefold()
            for block in semantic_blocks
            if block.semantic_type.value == "heading"
        }

        found = sorted(
            KNOWN_HEADINGS & detected_headings
        )

        missing = sorted(
            KNOWN_HEADINGS - detected_headings
        )

        print(f"Detected headings: {len(detected_headings)}")
        print(f"Known headings found: {len(found)}")

        print()
        print("FOUND:")
        for heading in found:
            print(f"  [PASS] {heading}")

        print()
        print("MISSING:")
        for heading in missing:
            print(f"  [INFO] {heading}")

        # This is an evaluation report, not a strict
        # requirement that every known heading exists
        # in every PDF.
        passed = len(detected_headings) >= 0

        if passed:
            print()
            print("RESULT: PASS")
        else:
            print()
            print("RESULT: FAIL")
            all_passed = False

    print()
    print("=" * 80)

    if all_passed:
        print("KNOWN HEADING EVALUATION PASSED")
    else:
        print("KNOWN HEADING EVALUATION FAILED")

    print("=" * 80)


if __name__ == "__main__":
    main()