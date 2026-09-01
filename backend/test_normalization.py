from app.models.document import normalize_text


def test_normalize_text():
    assert (
        normalize_text(
            "  Filing   Company:\tAmerican General  "
        )
        == "Filing Company: American General"
    )

    assert (
        normalize_text(
            "Table\nof\r\nContents"
        )
        == "Table of Contents"
    )

    assert normalize_text("   ") == ""

    assert (
        normalize_text(
            "P 22550-I [Expanded SOV] -redline.pdf"
        )
        == "P 22550-I [Expanded SOV] -redline.pdf"
    )


if __name__ == "__main__":
    test_normalize_text()

    print("=" * 60)
    print("NORMALIZATION TEST PASSED")
    print("=" * 60)