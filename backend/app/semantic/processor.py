from app.models.cleaning import CleanDocument
from app.models.semantic import SemanticBlock
from app.semantic.classifier import classify_block


def process_document(
    document: CleanDocument,
) -> list[SemanticBlock]:
    """
    Classify all blocks in a cleaned document.

    Noise blocks should already have been removed
    by the cleaning layer.
    """

    semantic_blocks: list[SemanticBlock] = []

    for page in document.pages:
        for block in page.blocks:
            semantic_block = classify_block(
                block=block,
                page_number=page.page_number,
            )

            semantic_blocks.append(
                semantic_block
            )

    return semantic_blocks