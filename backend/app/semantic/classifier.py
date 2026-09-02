import re
from app.models.document import Block
from app.models.semantic import SemanticBlock, SemanticType


KNOWN_HEADINGS = {
    "general information",
    "general filing information",
    "filing fees",
    "correspondence summary",
    "disposition",
    "objection letter",
    "response letter",
    "filing description",
    "supporting documents",
    "supporting document schedules",
    "attachments",
    "attachment(s)",
}

# Labels commonly found in SERFF metadata. These are deliberately NOT
# treated as headings because they are field labels, not document sections.
FIELD_LABEL_RE = re.compile(
    r"^(?:serff tracking #|state tracking #|company tracking #|"
    r"state|filing company|product name|project name/number|"
    r"toi/sub-toi|status date|item status|satisfied - item|"
    r"attachment\(s\)|comments|date submitted|score|attachments|submitted):?$",
    re.I,
)

NUMBERED_HEADING_RE = re.compile(
    r"^(?P<number>\d+(?:\.\d+){0,3})[.)]\s+(?P<title>[A-Za-z][^\n]{2,120})$"
)

SUBHEADING_RE = re.compile(
    r"^(?:objection|response|item|section)\s+\d+(?:\s*[:.-]\s*.*)?$",
    re.I,
)


def _clean(text: str) -> str:
    text = text.replace("\u00ad", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\s*\n\s*", " ", text)
    return text.strip()


def detect_heading_pattern(
    text: str,
) -> tuple[bool, float, dict[str, object]]:
    normalized = _clean(text)
    if not normalized:
        return False, 0.0, {}

    folded = normalized.casefold()

    # Field labels are metadata, never section headings.
    if FIELD_LABEL_RE.fullmatch(normalized):
        return False, 0.0, {"field_label": True}

    if folded in KNOWN_HEADINGS:
        return True, 0.98, {
            "heading_pattern": True,
            "heading_reason": "known_heading",
        }

    match = NUMBERED_HEADING_RE.fullmatch(normalized)
    if match:
        number = match.group("number")
        title = match.group("title").strip()
        if any(len(part) > 2 for part in number.split(".")):
            return False, 0.0, {}
        if len(title.split()) <= 16 and not re.search(r"[.!?]\s*$", title):
            return True, 0.90, {
                "heading_pattern": True,
                "heading_reason": "numbered_heading",
                "heading_level": len(number.split(".")),
            }

    if SUBHEADING_RE.fullmatch(normalized) and len(normalized.split()) <= 12:
        return True, 0.82, {
            "heading_pattern": True,
            "heading_reason": "document_subheading",
            "heading_level": 2,
        }

    return False, 0.0, {}


def classify_block(block: Block, page_number: int) -> SemanticBlock:
    text = block.text.strip()

    if not text:
        return SemanticBlock(
            page_number=page_number,
            source_block_index=block.raw_index,
            semantic_type=SemanticType.UNKNOWN,
            text="",
            confidence=1.0,
        )

    is_heading, confidence, heading_signals = detect_heading_pattern(text)

    if is_heading:
        return SemanticBlock(
            page_number=page_number,
            source_block_index=block.raw_index,
            semantic_type=SemanticType.HEADING,
            text=_clean(text),
            confidence=confidence,
            signals={
                **heading_signals,
                "indentation_level": block.layout.indentation_level,
                "repeated_x_position": block.layout.repeated_x_position,
            },
        )

    # Preserve explicit list/table evidence from the layout analyzer.
    if block.layout.is_list_like:
        return SemanticBlock(
            page_number=page_number,
            source_block_index=block.raw_index,
            semantic_type=SemanticType.LIST,
            text=_clean(text),
            confidence=0.86,
            signals={
                "list_like": True,
                "indentation_level": block.layout.indentation_level,
            },
        )

    if block.layout.is_table_like:
        return SemanticBlock(
            page_number=page_number,
            source_block_index=block.raw_index,
            semantic_type=SemanticType.TABLE,
            text=_clean(text),
            confidence=0.84,
            signals={
                "table_like": True,
                "repeated_x_position": block.layout.repeated_x_position,
            },
        )

    signals = {
        "content_type": "body_text",
        "indentation_level": block.layout.indentation_level,
    }

    if FIELD_LABEL_RE.fullmatch(_clean(text)):
        signals["content_type"] = "field_label"

    return SemanticBlock(
        page_number=page_number,
        source_block_index=block.raw_index,
        semantic_type=SemanticType.PARAGRAPH,
        text=_clean(text),
        confidence=0.80,
        signals=signals,
    )
