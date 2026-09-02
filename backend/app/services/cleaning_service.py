import re
from collections import Counter

from app.models.cleaning import CleanBlock, CleanDocument, CleanPage
from app.models.document import PDFDocument


def _normalize(text: str) -> str:
    text = text.replace("\u00ad", "")
    text = text.replace("\u2010", "-").replace("\u2011", "-").replace("\u2012", "-")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _dedupe_adjacent(blocks: list[CleanBlock]) -> list[CleanBlock]:
    result: list[CleanBlock] = []
    previous_key = None

    for block in blocks:
        key = re.sub(r"\s+", " ", block.text).strip().casefold()
        if key and key == previous_key:
            continue
        result.append(block)
        previous_key = key

    return result


def clean_document(document: PDFDocument) -> CleanDocument:
    """
    Clean the raw document without changing its source indices.

    Important design choice:
    We do NOT blindly merge every neighbouring block. SERFF pages contain
    forms, metadata fields, tables and letter text where aggressive merging
    destroys structure. We normalize text, remove known noise, deduplicate
    adjacent duplicates and preserve layout evidence for later semantic
    classification.
    """
    clean_document = CleanDocument()

    # Count exact normalized strings across pages. Very short repeated strings
    # are usually UI/header/footer artifacts; substantive text is preserved.
    all_text = []
    for page in document.pages:
        for block in page.visual_blocks:
            if block.noise_type.value == "none":
                value = _normalize(block.text)
                if value:
                    all_text.append(value.casefold())

    repeated = Counter(all_text)

    for page in document.pages:
        clean_page = CleanPage(page_number=page.page_number)
        candidates: list[CleanBlock] = []

        for block in page.visual_blocks:
            if block.noise_type.value != "none":
                continue

            text = _normalize(block.text)
            if not text:
                continue

            # Remove obvious page-number-only artifacts.
            if re.fullmatch(r"(?:page\s*)?\d{1,4}", text, re.I):
                continue

            # Keep repeated substantive content. Only extremely short repeated
            # fragments are suppressed when they are clearly noise-like.
            if (
                len(text) <= 3
                and repeated[text.casefold()] > 5
            ):
                continue

            candidates.append(
                CleanBlock(
                    page_number=page.page_number,
                    raw_index=block.raw_index,
                    text=text,
                    source_text=block.text,
                    layout=block.layout,
                )
            )

        clean_page.blocks.extend(_dedupe_adjacent(candidates))
        clean_document.pages.append(clean_page)

    return clean_document
