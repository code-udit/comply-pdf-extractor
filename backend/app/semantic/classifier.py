from app.models.document import Block
from app.models.semantic import SemanticBlock, SemanticType
import re

def detect_heading_pattern(text: str) -> tuple[bool, float]:
    """
    Detect common document heading patterns.

    Returns:
        (is_heading, confidence)
    """

    normalized = " ".join(text.split())

    if not normalized:
        return False, 0.0

    # Known major filing section names.
    known_headings = {
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

    if normalized.casefold() in known_headings:
        return True, 0.95

    # Numbered headings such as:
    # "1. General Information"
    # "2. Filing Description"
    if re.match(
        r"^\d+(?:\.\d+)*[.)]?\s+\S+",
        normalized,
    ):
        return True, 0.85

    return False, 0.0

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

    # Heading pattern detection.
    is_heading, heading_confidence = detect_heading_pattern(
        text
    )

    if is_heading:
        return SemanticBlock(
            page_number=page_number,
            source_block_index=block.raw_index,
            semantic_type=SemanticType.HEADING,
            text=text,
            confidence=heading_confidence,
            signals={
                "heading_pattern": True,
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