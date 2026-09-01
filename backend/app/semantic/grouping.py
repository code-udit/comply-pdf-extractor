from app.models.semantic import SemanticBlock, SemanticType
from app.models.section import Section

def get_heading_level(block: SemanticBlock) -> int:
    """
    Return the hierarchy level for a heading.

    The classifier may provide an explicit heading_level
    signal. Otherwise, default to level 1.
    """

    level = block.signals.get("heading_level", 1)

    if isinstance(level, int) and level >= 1:
        return level

    return 1

def group_semantic_blocks(
    semantic_blocks: list[SemanticBlock],
) -> list[Section]:
    """
    Group semantic blocks into a hierarchical section structure.

    Headings start sections.
    A lower-level heading becomes a child of the nearest
    preceding higher-level section.
    Non-heading blocks are attached to the current section.
    Content before the first heading is preserved.
    """

    sections: list[Section] = []
    section_stack: list[Section] = []
    current_section: Section | None = None

    for block in semantic_blocks:
        if block.semantic_type == SemanticType.HEADING:
            level = get_heading_level(block)

            new_section = Section(
                heading=block.text,
                level=level,
                page_start=block.page_number,
                page_end=block.page_number,
                blocks=[block],
            )

            while (
                section_stack
                and section_stack[-1].level >= level
            ):
                section_stack.pop()

            if section_stack:
                section_stack[-1].children.append(
                    new_section
                )
            else:
                sections.append(new_section)

            section_stack.append(new_section)
            current_section = new_section
            continue

        if current_section is None:
            current_section = Section(
                heading="",
                level=1,
                page_start=block.page_number,
                page_end=block.page_number,
                blocks=[block],
            )

            sections.append(current_section)
            section_stack = [current_section]
            continue

        current_section.blocks.append(block)
        current_section.page_end = block.page_number

    return sections