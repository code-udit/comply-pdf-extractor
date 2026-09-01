from collections import Counter

from app.models.document import Page


def analyze_page_layout_summary(page: Page) -> None:
    """
    Build a page-level summary from existing block layout signals.
    """

    blocks = page.visual_blocks

    summary = page.layout_summary

    summary.block_count = len(blocks)

    if not blocks:
        return

    # Content boundaries
    summary.content_top = min(
        block.y0
        for block in blocks
    )

    summary.content_bottom = max(
        block.y1
        for block in blocks
    )

    # Repeated horizontal positions
    x_positions = [
        round(block.x0, 1)
        for block in blocks
    ]

    counts = Counter(x_positions)

    summary.repeated_x_positions = sorted(
        x
        for x, count in counts.items()
        if count >= 2
    )

    # Layout signal counts
    summary.list_like_blocks = sum(
        1
        for block in blocks
        if block.layout.is_list_like
    )

    summary.table_like_blocks = sum(
        1
        for block in blocks
        if block.layout.is_table_like
    )

    # Noise counts
    summary.header_blocks = sum(
        1
        for block in blocks
        if block.noise_type.value == "header"
    )

    summary.footer_blocks = sum(
        1
        for block in blocks
        if block.noise_type.value == "footer"
    )