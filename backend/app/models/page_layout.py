from dataclasses import dataclass, field


@dataclass
class PageLayoutSummary:
    """
    Page-level geometric and structural summary.

    These are layout measurements/signals only.
    """

    block_count: int = 0

    content_top: float | None = None
    content_bottom: float | None = None

    repeated_x_positions: list[float] = field(
        default_factory=list
    )

    list_like_blocks: int = 0
    table_like_blocks: int = 0

    header_blocks: int = 0
    footer_blocks: int = 0