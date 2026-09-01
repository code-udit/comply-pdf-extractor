from collections import Counter

from app.models.document import Block, Page


X_TOLERANCE = 8.0


def approximately_equal(
    first: float,
    second: float,
    tolerance: float = X_TOLERANCE,
) -> bool:
    return abs(first - second) <= tolerance


def detect_indentation(
    block: Block,
    page: Page,
) -> int:
    """
    Estimate indentation relative to the page.
    """

    if block.x0 < page.width * 0.20:
        return 0

    if block.x0 < page.width * 0.35:
        return 1

    if block.x0 < page.width * 0.50:
        return 2

    return 3


def detect_list_like(block: Block) -> bool:
    """
    Detect simple list-style prefixes.
    """

    text = block.normalized_text

    if not text:
        return False

    prefixes = (
        "- ",
        "* ",
        "• ",
        "– ",
    )

    if text.startswith(prefixes):
        return True

    if len(text) >= 2:
        first_space = text.find(" ")

        if first_space > 0:
            prefix = text[:first_space]

            if prefix[:-1].isdigit() and prefix.endswith("."):
                return True

    return False


def detect_table_like(
    block: Block,
    repeated_x_positions: list[float],
) -> bool:
    """
    Detect evidence of tabular alignment.
    """

    if len(repeated_x_positions) < 2:
        return False

    line_x_positions = []

    for line in block.lines:
        for span in line.spans:
            line_x_positions.append(span.x0)

    matches = 0

    for x in line_x_positions:
        for repeated_x in repeated_x_positions:
            if approximately_equal(x, repeated_x):
                matches += 1
                break

    return matches >= 2


def analyze_page_layout(page: Page) -> None:
    """
    Calculate layout signals for a page.
    """

    blocks = page.visual_blocks

    if not blocks:
        return

    x_positions = [
        round(block.x0, 1)
        for block in blocks
    ]

    counts = Counter(x_positions)

    repeated_x_positions = [
        x
        for x, count in counts.items()
        if count >= 2
    ]

    midpoint = page.width / 2

    for block in blocks:

        block.layout.left_x = block.x0
        block.layout.right_x = block.x1

        block.layout.indentation_level = detect_indentation(
            block=block,
            page=page,
        )

        block.layout.is_list_like = detect_list_like(block)

        block.layout.repeated_x_position = any(
            approximately_equal(
                block.x0,
                repeated_x,
            )
            for repeated_x in repeated_x_positions
        )

        block.layout.is_table_like = detect_table_like(
            block=block,
            repeated_x_positions=repeated_x_positions,
        )

        if block.x0 < midpoint:
            block.layout.column_index = 0
        else:
            block.layout.column_index = 1