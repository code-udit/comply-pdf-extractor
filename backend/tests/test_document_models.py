from app.models.document import normalize_text, Span


def test_normalize_text_collapses_whitespace():
    assert normalize_text("hello   world") == "hello world"


def test_normalize_text_replaces_tabs_and_newlines():
    assert normalize_text("hello\tworld\nfoo\rbar") == "hello world foo bar"


def test_normalize_text_strips_leading_trailing_whitespace():
    assert normalize_text("   hello world   ") == "hello world"


def test_normalize_text_empty_string_returns_empty():
    assert normalize_text("") == ""


def test_normalize_text_none_like_falsy_returns_empty():
    assert normalize_text(None) == ""  # type: ignore[arg-type]


def test_span_normalized_text_property():
    span = Span(
        index=0,
        text="  Hello \n World  ",
        bbox=(0.0, 0.0, 10.0, 10.0),
        font="Helvetica",
        font_size=12.0,
        flags=0,
    )
    assert span.normalized_text == "Hello World"
