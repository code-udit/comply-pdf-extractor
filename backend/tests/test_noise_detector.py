from pathlib import Path

from app.extraction.noise_detector import (
    classify_page_noise,
    matches_pattern,
    SERFF_HEADER_PATTERNS,
    FOOTER_PATTERNS,
)
from app.extraction.raw_extractor import RawPDFExtractor
from app.models.document import NoiseType


def test_matches_pattern_true_for_known_header():
    assert matches_pattern(
        "SERFF Tracking #: ABCD-123456789", SERFF_HEADER_PATTERNS
    )


def test_matches_pattern_false_for_body_text():
    assert not matches_pattern(
        "Rate filing summary for review.", SERFF_HEADER_PATTERNS
    )


def test_matches_pattern_true_for_footer():
    assert matches_pattern(
        "PDF Pipeline for SERFF Tracking Number ABCD-123 Generated 01/01/2026",
        FOOTER_PATTERNS,
    )


def test_classify_page_noise_flags_header_and_footer(serff_style_pdf: Path):
    document = RawPDFExtractor(serff_style_pdf).extract()
    page = document.pages[0]

    classify_page_noise(page)

    noise_types = {block.noise_type for block in page.blocks}
    assert NoiseType.HEADER in noise_types
    assert NoiseType.FOOTER in noise_types
    # The body text block should remain unflagged.
    assert NoiseType.NONE in noise_types


def test_classify_page_noise_leaves_plain_page_untouched(simple_pdf: Path):
    document = RawPDFExtractor(simple_pdf).extract()
    page = document.pages[0]

    classify_page_noise(page)

    assert all(block.noise_type == NoiseType.NONE for block in page.blocks)
