from fastapi import HTTPException, UploadFile


MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB
PDF_CONTENT_TYPE = "application/pdf"


class PDFValidationError(HTTPException):
    """Raised when an uploaded PDF fails validation."""

    def __init__(
        self,
        message: str,
        status_code: int = 400,
        request_id: str | None = None,
    ) -> None:
        self.request_id = request_id

        super().__init__(
            status_code=status_code,
            detail=message,
        )


async def validate_pdf_upload(
    file: UploadFile,
    request_id: str | None = None,
) -> bytes:
    """
    Validate an uploaded PDF and return its bytes.

    Validation includes:
    - filename presence
    - .pdf extension
    - PDF MIME type when provided
    - non-empty content
    - maximum file size
    """

    if not file.filename:
        raise PDFValidationError(
            "A filename is required.",
            request_id=request_id,
        )

    if not file.filename.lower().endswith(".pdf"):
        raise PDFValidationError(
            "Only PDF files are supported.",
            request_id=request_id,
        )

    if (
        file.content_type
        and file.content_type != PDF_CONTENT_TYPE
    ):
        raise PDFValidationError(
            "Uploaded file must have application/pdf content type.",
            request_id=request_id,
        )

    content = await file.read()

    if not content:
        raise PDFValidationError(
            "Uploaded PDF is empty.",
            request_id=request_id,
        )

    if len(content) > MAX_FILE_SIZE:
        raise PDFValidationError(
            "Uploaded PDF exceeds the 25 MB size limit.",
            status_code=413,
            request_id=request_id,
        )

    return content