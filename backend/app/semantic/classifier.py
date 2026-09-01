import re

from app.models.document import Block
from app.models.semantic import SemanticBlock, SemanticType


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


def detect_heading_pattern(
    text: str,
) -> tuple[bool, float, dict[str, object]]:
    """
    Detect strong document heading patterns.

    Heading detection is intentionally conservative.
    """

    normalized = " ".join(text.split())

    if not normalized:
        return False, 0.0, {}

    folded = normalized.casefold()

    # Strong signal: known filing section heading.
    if folded in KNOWN_HEADINGS:
        return (
            True,
            0.95,
            {
                "heading_pattern": True,
                "heading_reason": "known_heading",
            },
        )

    # Numbered headings must contain a meaningful title.
    #
    # Accepted:
    #   1. General Information
    #   2) Filing Description
    #   1.2 Filing Details
    #
    # Rejected:
    #   2021 under SERFF tracking number...
    #   134334281) Attachment(s):
    numbered_match = re.match(
        r"^(?P<number>\d+(?:\.\d+)*)(?:[.)])\s+"
        r"(?P<title>[A-Za-z][^\n]{2,120})$",
        normalized,
    )

    if numbered_match:
        number = numbered_match.group("number")
        title = numbered_match.group("title").strip()

        # Section numbers should be structurally small.
        # Reject tracking/reference numbers such as:
        #   134334281) Attachment(s):
        number_parts = number.split(".")

        if any(len(part) > 2 for part in number_parts):
            return False, 0.0, {}

        if (
            len(title.split()) <= 16
            and not re.search(r"[.!?]\s*$", title)
        ):
            level = len(number_parts)

            return (
                True,
                0.85,
                {
                    "heading_pattern": True,
                    "heading_reason": "numbered_heading",
                    "heading_level": level,
                },
            )

    return False, 0.0, {}


def classify_block(
    block: Block,
    page_number: int,
) -> SemanticBlock:
    """
    Classify one cleaned document block.

    Strong semantic heading patterns take precedence over
    layout-based table/list detection.
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

    # Heading detection comes first so that known headings
    # are not incorrectly classified as tables or lists.
    is_heading, heading_confidence, heading_signals = (
        detect_heading_pattern(text)
    )

    if is_heading:
        return SemanticBlock(
            page_number=page_number,
            source_block_index=block.raw_index,
            semantic_type=SemanticType.HEADING,
            text=text,
            confidence=heading_confidence,
            signals={
                **heading_signals,
                "indentation_level": (
                    block.layout.indentation_level
                ),
                "repeated_x_position": (
                    block.layout.repeated_x_position
                ),
            },
        )

    # Strong signal: list-like layout.
    if block.layout.is_list_like:
        return SemanticBlock(
            page_number=page_number,
            source_block_index=block.raw_index,
            semantic_type=SemanticType.LIST,
            text=text,
            confidence=0.80,
            signals={
                "list_like": True,
                "indentation_level": (
                    block.layout.indentation_level
                ),
            },
        )

    # Strong signal: table-like layout.
    if block.layout.is_table_like:
        return SemanticBlock(
            page_number=page_number,
            source_block_index=block.raw_index,
            semantic_type=SemanticType.TABLE,
            text=text,
            confidence=0.80,
            signals={
                "table_like": True,
                "repeated_x_position": (
                    block.layout.repeated_x_position
                ),
            },
        )

    # Ordinary extracted text is body content.
    return SemanticBlock(
        page_number=page_number,
        source_block_index=block.raw_index,
        semantic_type=SemanticType.PARAGRAPH,
        text=text,
        confidence=0.75,
        signals={
            "content_type": "body_text",
            "indentation_level": (
                block.layout.indentation_level
            ),
        },
    )