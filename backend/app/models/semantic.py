from dataclasses import dataclass, field
from enum import Enum


class SemanticType(str, Enum):
    """High-level semantic classification of document content."""

    UNKNOWN = "unknown"
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    TABLE = "table"
    LIST = "list"
    FORM_FIELD = "form_field"
    ATTACHMENT = "attachment"


@dataclass
class SemanticBlock:
    """Semantic representation of a cleaned document block."""

    page_number: int
    source_block_index: int
    semantic_type: SemanticType = SemanticType.UNKNOWN

    text: str = ""

    confidence: float = 0.0

    signals: dict[str, object] = field(
        default_factory=dict
    )