from app.models.cleaning import (
    CleanBlock,
    CleanDocument,
    CleanPage,
)
from app.models.document import PDFDocument


def clean_document(document: PDFDocument) -> CleanDocument:
    """
    Create a cleaned representation without modifying the raw document.

    Noise blocks are excluded from the cleaned pages.
    Original block text is preserved in source_text.
    """

    clean_document = CleanDocument()

    for page in document.pages:
        clean_page = CleanPage(
            page_number=page.page_number
        )

        for block in page.visual_blocks:
            source_text = block.text

            if block.noise_type.value != "none":
                continue

            text = block.normalized_text

            if not text:
                continue

            clean_block = CleanBlock(
                page_number=page.page_number,
                raw_index=block.raw_index,
                text=text,
                source_text=source_text,
            )

            clean_page.blocks.append(clean_block)

        clean_document.pages.append(clean_page)

    return clean_document