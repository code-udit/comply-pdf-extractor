from app.models.section import Section
from app.models.semantic import SemanticBlock, SemanticType


TOP_LEVEL_HEADINGS = {
    "general filing information",
    "general information",
    "filing fees",
    "correspondence summary",
    "disposition",
    "objection letter",
    "response letter",
    "filing description",
    "supporting documents",
    "supporting document schedules",
    "attachments",
}


def normalize_heading(text: str) -> str:
    return " ".join(text.split()).strip()


def canonical_heading(text: str) -> str:
    """
    Normalize known top-level headings.

    This prevents minor extraction differences from creating
    duplicate sections.
    """

    normalized = normalize_heading(text)
    folded = normalized.casefold()

    aliases = {
        "general filing information": "General Filing Information",
        "general information": "General Information",
        "filing fees": "Filing Fees",
        "correspondence summary": "Correspondence Summary",
        "disposition": "Disposition",
        "response letter": "Response Letter",
        "supporting documents": "Supporting Documents",
        "supporting document schedules": "Supporting Document Schedules",
        "objection letter": "Objection Letter",
        "filing description": "Filing Description",
        "attachments": "Attachments",
    }

    return aliases.get(folded, normalized)


def is_top_level_heading(block: SemanticBlock) -> bool:
    """
    Only known document-level headings are allowed to create
    top-level sections.

    Important:
    'Objection 1', 'Objection 2', 'Response 1', etc. are
    document content and must NOT create new top-level sections.
    """

    if block.semantic_type != SemanticType.HEADING:
        return False

    text = normalize_heading(block.text)

    if not text:
        return False

    return text.casefold() in TOP_LEVEL_HEADINGS


def create_section(
    heading: str,
    block: SemanticBlock,
) -> Section:
    return Section(
        heading=canonical_heading(heading),
        level=1,
        page_start=block.page_number,
        page_end=block.page_number,
        blocks=[],
        children=[],
    )


def add_block(
    section: Section,
    block: SemanticBlock,
) -> None:
    section.blocks.append(block)

    if section.page_start is None:
        section.page_start = block.page_number

    if section.page_end is None:
        section.page_end = block.page_number
    else:
        section.page_end = max(
            section.page_end,
            block.page_number,
        )


def group_semantic_blocks(
    semantic_blocks: list[SemanticBlock],
) -> list[Section]:
    """
    Build top-level document sections while preserving every block.

    Design rules:

    1. Every block must belong to exactly one section.
    2. Only known top-level headings start sections.
    3. Internal headings such as 'Objection 1' and 'Response 1'
       remain content inside their parent section.
    4. Repeated top-level headings are treated as continuation
       headers instead of creating duplicate sections.
    5. Content before the first known heading belongs to
       General Filing Information.
    """

    if not semantic_blocks:
        return []

    sections: list[Section] = []
    current_section: Section | None = None

    # Keep track of sections already created so repeated PDF
    # headers do not generate duplicate top-level sections.
    section_by_heading: dict[str, Section] = {}

    for block in semantic_blocks:

        # ---------------------------------------------------------
        # TOP-LEVEL HEADING
        # ---------------------------------------------------------

        if is_top_level_heading(block):
            heading = canonical_heading(block.text)
            key = heading.casefold()

            # If this heading already exists, it is probably a
            # repeated header on a later page. Keep using the
            # existing section rather than creating another one.
            if key in section_by_heading:
                current_section = section_by_heading[key]

                # The heading itself is still important content,
                # so preserve it in the section.
                add_block(current_section, block)

                continue

            # First occurrence of a genuine top-level section.
            current_section = create_section(
                heading,
                block,
            )

            sections.append(current_section)
            section_by_heading[key] = current_section

            add_block(current_section, block)

            continue

        # ---------------------------------------------------------
        # CONTENT BEFORE FIRST TOP-LEVEL HEADING
        # ---------------------------------------------------------

        if current_section is None:
            current_section = section_by_heading.get(
                "general filing information"
            )

            if current_section is None:
                current_section = Section(
                    heading="General Filing Information",
                    level=1,
                    page_start=block.page_number,
                    page_end=block.page_number,
                    blocks=[],
                    children=[],
                )

                sections.append(current_section)

                section_by_heading[
                    "general filing information"
                ] = current_section

        # ---------------------------------------------------------
        # ALL NON-TOP-LEVEL CONTENT
        #
        # This includes:
        #
        # - paragraphs
        # - tables
        # - lists
        # - Objection 1
        # - Objection 2
        # - Response 1
        # - Response 2
        # - other internal headings
        #
        # Nothing is discarded.
        # ---------------------------------------------------------

        add_block(
            current_section,
            block,
        )

    return sections