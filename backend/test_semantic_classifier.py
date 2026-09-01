from app.models.document import Block, Line, Span
from app.models.semantic import SemanticType
from app.semantic.classifier import classify_block


def main():
    print("=" * 60)
    print("SEMANTIC CLASSIFIER TEST")
    print("=" * 60)

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

    print()
    print("=" * 60)
    print("SEMANTIC CLASSIFIER TEST PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()