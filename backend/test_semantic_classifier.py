from app.models.document import Block, Line, Span
from app.models.semantic import SemanticType
from app.semantic.classifier import (
    classify_block,
    detect_heading_pattern,
)


def main():
    print("=" * 60)
    print("SEMANTIC CLASSIFIER TEST")
    print("=" * 60)

    # Existing unknown case
    block = Block(
        raw_index=5,
        bbox=(25.0, 100.0, 200.0, 120.0),
    )

    block.layout.is_table_like = False

    block.lines = [
        Line(
            index=0,
            bbox=(25.0, 100.0, 200.0, 120.0),
            spans=[
                Span(
                    index=0,
                    text="Example table content",
                    bbox=(25.0, 100.0, 200.0, 120.0),
                    font="Helvetica",
                    font_size=10.0,
                    flags=0,
                )
            ],
        )
    ]

    result = classify_block(
        block=block,
        page_number=1,
    )

    print(f"Type:       {result.semantic_type.value}")
    print(f"Text:       {result.text}")
    print(f"Confidence: {result.confidence}")
    print(f"Signals:    {result.signals}")

    assert result.semantic_type == SemanticType.UNKNOWN
    assert result.confidence == 0.5
    assert result.signals == {}

    # Heading case
    heading_block = Block(
        raw_index=6,
        bbox=(25.0, 130.0, 300.0, 150.0),
    )

    heading_block.layout.is_table_like = False
    heading_block.layout.is_list_like = False

    heading_block.lines = [
        Line(
            index=0,
            bbox=(25.0, 130.0, 300.0, 150.0),
            spans=[
                Span(
                    index=0,
                    text="General Information",
                    bbox=(25.0, 130.0, 300.0, 150.0),
                    font="Helvetica",
                    font_size=10.0,
                    flags=0,
                )
            ],
        )
    ]

    heading_result = classify_block(
        block=heading_block,
        page_number=1,
    )

    print()
    print(f"Heading Type:       {heading_result.semantic_type.value}")
    print(f"Heading Text:       {heading_result.text}")
    print(f"Heading Confidence: {heading_result.confidence}")
    print(f"Heading Signals:    {heading_result.signals}")

    assert heading_result.semantic_type == SemanticType.HEADING
    assert heading_result.confidence == 0.95
    assert heading_result.signals == {
        "heading_pattern": True,
    }

    # Known heading patterns
    known_headings = [
        "General Information",
        "Filing Fees",
        "Correspondence Summary",
        "Disposition",
        "Objection Letter",
        "Response Letter",
        "Filing Description",
        "Supporting Documents",
        "Attachments",
    ]

    for heading in known_headings:
        detected, confidence = detect_heading_pattern(
            heading
        )

        assert detected is True
        assert confidence == 0.95

    # Numbered heading patterns
    numbered_headings = [
        "1. General Information",
        "2. Filing Description",
        "3. Supporting Documents",
    ]

    for heading in numbered_headings:
        detected, confidence = detect_heading_pattern(
            heading
        )

        assert detected is True
        assert confidence == 0.85

    # Non-heading patterns
    non_headings = [
        "This is a normal paragraph containing filing information.",
        "The company submitted the requested documents for review.",
        "Additional information is provided below.",
        "Example table content",
        "Please review the attached supporting documentation.",
    ]

    for text in non_headings:
        detected, confidence = detect_heading_pattern(
            text
        )

        assert detected is False
        assert confidence == 0.0

    print()
    print("=" * 60)
    print("SEMANTIC CLASSIFIER TEST PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()