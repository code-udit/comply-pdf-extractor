import re

from app.models.document import (
    Block,
    NoiseType,
    Page,
)


SERFF_HEADER_PATTERNS = (
    r"^SERFF Tracking #",
    r"^State Tracking #",
    r"^Company Tracking #",
    r"^State:",
    r"^Filing Company:",
    r"^TOI/Sub-TOI:",
    r"^Product Name:",
    r"^Project Name/Number:",
)


FOOTER_PATTERNS = (
    r"^PDF Pipeline for SERFF Tracking Number",
    r"Generated \d{2}/\d{2}/\d{4}",
)


def matches_pattern(
    text: str,
    patterns: tuple[str, ...],
) -> bool:
    """Return True when text matches one of the patterns."""

    for pattern in patterns:
        if re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        ):
            return True

    return False


def detect_block_noise(
    block: Block,
    page: Page,
) -> tuple[NoiseType, str | None]:
    """
    Detect likely header/footer noise.

    This function only classifies the block.
    It does not delete or modify it.
    """

    text = block.normalized_text

    if not text:
        return NoiseType.NONE, None

    # Footer detection.
    if block.y0 >= page.height * 0.90:
        if matches_pattern(
            text,
            FOOTER_PATTERNS,
        ):
            return (
                NoiseType.FOOTER,
                "SERFF PDF pipeline footer",
            )

    # Header detection.
    if block.y0 <= page.height * 0.15:
        if matches_pattern(
            text,
            SERFF_HEADER_PATTERNS,
        ):
            return (
                NoiseType.HEADER,
                "SERFF filing metadata header",
            )

    return NoiseType.NONE, None


def classify_page_noise(page: Page) -> None:
    """Classify noise blocks on a page."""

    for block in page.blocks:
        noise_type, reason = detect_block_noise(
            block=block,
            page=page,
        )

        block.noise_type = noise_type
        block.noise_reason = reason