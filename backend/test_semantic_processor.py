from pathlib import Path

from app.extraction.raw_extractor import RawPDFExtractor
from app.extraction.noise_detector import classify_page_noise
from app.extraction.layout_analyzer import analyze_page_layout
from app.services.cleaning_service import clean_document
from app.semantic.processor import process_document


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PDF_PATH = (
    PROJECT_ROOT
    / "sample_documents"
    / "AMGN-135003565.pdf"
)


def main():
    print("=" * 60)
    print("SEMANTIC PROCESSOR TEST")
    print("=" * 60)

    extractor = RawPDFExtractor(PDF_PATH)
    document = extractor.extract()

    for page in document.pages:
        classify_page_noise(page)
        analyze_page_layout(page)

    cleaned_document = clean_document(document)

    semantic_blocks = process_document(
        cleaned_document
    )

    print()
    print(f"Clean pages:       {len(cleaned_document.pages)}")
    print(f"Semantic blocks:   {len(semantic_blocks)}")

    assert len(cleaned_document.pages) == 15
    assert len(semantic_blocks) == 280

    print()
    print("=" * 60)
    print("SEMANTIC PROCESSOR TEST PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()