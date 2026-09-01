from pathlib import Path

from app.extraction.pdf_loader import PDFLoader


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PDF_PATH = PROJECT_ROOT / "sample_documents" / "AMGN-135003565.pdf"


def main():
    print("=" * 70)
    print("PDF LOADER TEST")
    print("=" * 70)

    print(f"PDF: {PDF_PATH}")
    print(f"Exists: {PDF_PATH.exists()}")

    loader = PDFLoader(PDF_PATH)

    page_count = loader.get_page_count()

    print(f"Page count: {page_count}")

    print("\n" + "-" * 70)
    print("PAGE 1 TEXT")
    print("-" * 70)

    text = loader.get_page_text(1)

    print(text)

    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()