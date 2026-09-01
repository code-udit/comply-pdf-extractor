from dataclasses import dataclass, field


@dataclass
class Section:
    """
    Structured document section built from semantic blocks.
    """

    heading: str = ""

    level: int = 1

    page_start: int | None = None
    page_end: int | None = None

    blocks: list[object] = field(
        default_factory=list
    )

    children: list["Section"] = field(
        default_factory=list
    )