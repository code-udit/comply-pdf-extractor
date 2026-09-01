from app.models.semantic import SemanticBlock, SemanticType
from app.semantic.grouping import (
    get_heading_level,
    group_semantic_blocks,
)

def test_heading_levels():
    heading = SemanticBlock(
        page_number=1,
        source_block_index=0,
        semantic_type=SemanticType.HEADING,
        text="Subheading",
        confidence=0.9,
        signals={
            "heading_level": 2,
        },
    )

    assert get_heading_level(heading) == 2

    default_heading = SemanticBlock(
        page_number=1,
        source_block_index=1,
        semantic_type=SemanticType.HEADING,
        text="Main Heading",
        confidence=0.9,
    )

    assert get_heading_level(default_heading) == 1

def test_nested_sections():
    blocks = [
        SemanticBlock(
            page_number=1,
            source_block_index=0,
            semantic_type=SemanticType.HEADING,
            text="General Information",
            confidence=0.9,
            signals={
                "heading_level": 1,
            },
        ),
        SemanticBlock(
            page_number=1,
            source_block_index=1,
            semantic_type=SemanticType.PARAGRAPH,
            text="General information body.",
            confidence=0.9,
        ),
        SemanticBlock(
            page_number=1,
            source_block_index=2,
            semantic_type=SemanticType.HEADING,
            text="Company and Contact",
            confidence=0.9,
            signals={
                "heading_level": 2,
            },
        ),
        SemanticBlock(
            page_number=1,
            source_block_index=3,
            semantic_type=SemanticType.PARAGRAPH,
            text="Company contact information.",
            confidence=0.9,
        ),
        SemanticBlock(
            page_number=2,
            source_block_index=4,
            semantic_type=SemanticType.HEADING,
            text="Filing Description",
            confidence=0.9,
            signals={
                "heading_level": 1,
            },
        ),
    ]

    sections = group_semantic_blocks(blocks)

    assert len(sections) == 2

    assert sections[0].heading == "General Information"
    assert sections[0].level == 1
    assert len(sections[0].children) == 1

    child = sections[0].children[0]

    assert child.heading == "Company and Contact"
    assert child.level == 2
    assert len(child.blocks) == 2

    assert sections[1].heading == "Filing Description"
    assert sections[1].level == 1

def test_three_level_hierarchy():
    blocks = [
        SemanticBlock(
            page_number=1,
            source_block_index=0,
            semantic_type=SemanticType.HEADING,
            text="General Information",
            confidence=0.9,
            signals={"heading_level": 1},
        ),
        SemanticBlock(
            page_number=1,
            source_block_index=1,
            semantic_type=SemanticType.HEADING,
            text="Company and Contact",
            confidence=0.9,
            signals={"heading_level": 2},
        ),
        SemanticBlock(
            page_number=1,
            source_block_index=2,
            semantic_type=SemanticType.HEADING,
            text="Primary Contact",
            confidence=0.9,
            signals={"heading_level": 3},
        ),
        SemanticBlock(
            page_number=1,
            source_block_index=3,
            semantic_type=SemanticType.PARAGRAPH,
            text="Contact details.",
            confidence=0.9,
        ),
    ]

    sections = group_semantic_blocks(blocks)

    assert len(sections) == 1

    level_one = sections[0]
    assert level_one.heading == "General Information"
    assert level_one.level == 1
    assert len(level_one.children) == 1

    level_two = level_one.children[0]
    assert level_two.heading == "Company and Contact"
    assert level_two.level == 2
    assert len(level_two.children) == 1

    level_three = level_two.children[0]
    assert level_three.heading == "Primary Contact"
    assert level_three.level == 3
    assert len(level_three.blocks) == 2

def test_nested_page_ranges():
    blocks = [
        SemanticBlock(
            page_number=1,
            source_block_index=0,
            semantic_type=SemanticType.HEADING,
            text="General Information",
            confidence=0.9,
            signals={"heading_level": 1},
        ),
        SemanticBlock(
            page_number=2,
            source_block_index=1,
            semantic_type=SemanticType.PARAGRAPH,
            text="General information continues.",
            confidence=0.9,
        ),
        SemanticBlock(
            page_number=3,
            source_block_index=2,
            semantic_type=SemanticType.HEADING,
            text="Company Details",
            confidence=0.9,
            signals={"heading_level": 2},
        ),
        SemanticBlock(
            page_number=4,
            source_block_index=3,
            semantic_type=SemanticType.PARAGRAPH,
            text="Company details continue.",
            confidence=0.9,
        ),
    ]

    sections = group_semantic_blocks(blocks)

    assert len(sections) == 1

    parent = sections[0]
    assert parent.page_start == 1
    assert parent.page_end == 2

    child = parent.children[0]
    assert child.page_start == 3
    assert child.page_end == 4

def main():
    test_nested_sections()
    test_three_level_hierarchy()
    test_nested_page_ranges()
    test_heading_levels()
    print("=" * 60)
    print("BODY GROUPING TEST")
    print("=" * 60)

    blocks = [
        SemanticBlock(
            page_number=1,
            source_block_index=0,
            semantic_type=SemanticType.PARAGRAPH,
            text="Introductory filing information.",
            confidence=0.9,
        ),
        SemanticBlock(
            page_number=1,
            source_block_index=1,
            semantic_type=SemanticType.HEADING,
            text="General Information",
            confidence=0.9,
        ),
        SemanticBlock(
            page_number=1,
            source_block_index=2,
            semantic_type=SemanticType.PARAGRAPH,
            text="Company information goes here.",
            confidence=0.9,
        ),
        SemanticBlock(
            page_number=1,
            source_block_index=3,
            semantic_type=SemanticType.LIST,
            text="• Filing item one",
            confidence=0.8,
        ),
        SemanticBlock(
            page_number=1,
            source_block_index=4,
            semantic_type=SemanticType.TABLE,
            text="Field | Value",
            confidence=0.8,
        ),
        SemanticBlock(
            page_number=1,
            source_block_index=3,
            semantic_type=SemanticType.PARAGRAPH,
            text="Additional filing information.",
            confidence=0.9,
        ),
        SemanticBlock(
            page_number=2,
            source_block_index=4,
            semantic_type=SemanticType.HEADING,
            text="Filing Description",
            confidence=0.9,
        ),
        SemanticBlock(
            page_number=2,
            source_block_index=5,
            semantic_type=SemanticType.PARAGRAPH,
            text="The purpose of this filing is...",
            confidence=0.9,
        ),
        SemanticBlock(
            page_number=2,
            source_block_index=6,
            semantic_type=SemanticType.PARAGRAPH,
            text="Additional text after the final heading.",
            confidence=0.9,
        ),
    ]

    sections = group_semantic_blocks(blocks)

    print(f"Sections: {len(sections)}")

    for section in sections:
        print(
            f"Section: {section.heading} | "
            f"blocks={len(section.blocks)} | "
            f"pages={section.page_start}-{section.page_end}"
        )

    assert len(sections) == 3

    assert sections[0].heading == ""
    assert len(sections[0].blocks) == 1
    assert sections[0].blocks[0].text == (
        "Introductory filing information."
    )

    assert sections[1].heading == "General Information"
    assert len(sections[1].blocks) == 5
    assert sections[1].page_start == 1
    assert sections[1].page_end == 1

    assert sections[2].heading == "Filing Description"
    assert len(sections[2].blocks) == 3
    assert sections[2].page_end == 2
    assert sections[2].blocks[2].text == (
        "Additional text after the final heading."
    )
    assert sections[2].page_start == 2
    assert sections[2].page_end == 2

    print()
    print("=" * 60)
    print("BODY GROUPING TEST PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()