from app.models.document import Block
from app.models.semantic import SemanticBlock, SemanticType


def classify_block(
    block: Block,
    page_number: int,
) -> SemanticBlock:
    """
    Classify one cleaned PDF block at a high level.

    This is intentionally conservative.
    """

    text = block.text.strip()

    if not text:
        return SemanticBlock(
            page_number=page_number,
            source_block_index=block.raw_index,
            semantic_type=SemanticType.UNKNOWN,
            text=text,
            confidence=1.0,
        )

    # Strong signal: list-like layout.
    if block.layout.is_list_like:
        return SemanticBlock(
            page_number=page_number,
            source_block_index=block.raw_index,
            semantic_type=SemanticType.LIST,
            text=text,
            confidence=0.8,
            signals={
                "list_like": True,
            },
        )

    # Strong signal: table-like layout.
    if block.layout.is_table_like:
        return SemanticBlock(
            page_number=page_number,
            source_block_index=block.raw_index,
            semantic_type=SemanticType.TABLE,
            text=text,
            confidence=0.8,
            signals={
                "table_like": True,
            },
        )

    # Default: preserve content as an unknown semantic block.
    return SemanticBlock(
        page_number=page_number,
        source_block_index=block.raw_index,
        semantic_type=SemanticType.UNKNOWN,
        text=text,
        confidence=0.5,
    )