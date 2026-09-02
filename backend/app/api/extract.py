import tempfile
import time
import uuid
from pathlib import Path

from fastapi import APIRouter, UploadFile

from app.api.validation import validate_pdf_upload
from app.extraction.raw_extractor import RawPDFExtractor
from app.semantic.grouping import group_semantic_blocks
from app.semantic.processor import process_document
from app.services.cleaning_service import clean_document


router = APIRouter(prefix="/api", tags=["extraction"])


def serialize_section(section) -> dict:
    return {
        "heading": section.heading,
        "level": section.level,
        "page_start": section.page_start,
        "page_end": section.page_end,
        "blocks": [
            {
                "page_number": block.page_number,
                "source_block_index": block.source_block_index,
                "semantic_type": block.semantic_type.value,
                "text": block.text,
                "confidence": round(block.confidence, 2),
                "signals": block.signals,
            }
            for block in section.blocks
        ],
        "children": [serialize_section(child) for child in section.children],
    }


@router.post("/extract")
async def extract_pdf(file: UploadFile):
    start_time = time.perf_counter()
    request_id = str(uuid.uuid4())

    pdf_bytes = await validate_pdf_upload(file, request_id=request_id)
    temporary_path: Path | None = None

    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temporary_file:
            temporary_file.write(pdf_bytes)
            temporary_path = Path(temporary_file.name)

        raw_document = RawPDFExtractor(temporary_path).extract()
        cleaned_document = clean_document(raw_document)
        semantic_blocks = process_document(cleaned_document)
        sections = group_semantic_blocks(semantic_blocks)

        processing_time_ms = (time.perf_counter() - start_time) * 1000

        return {
            "metadata": {
                "request_id": request_id,
                "filename": file.filename,
                "page_count": raw_document.page_count,
                "processing_time_ms": round(processing_time_ms, 2),
                "block_count": len(semantic_blocks),
            },
            "sections": [serialize_section(section) for section in sections],
        }

    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
