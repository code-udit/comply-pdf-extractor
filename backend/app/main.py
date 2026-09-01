from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.extract import router as extraction_router
from app.api.validation import PDFValidationError
from app.models.api import ErrorResponse, HealthResponse


app = FastAPI(
    title="Comply PDF Extractor API",
    description="API for extracting structured engineering requirements from compliance PDFs.",
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(extraction_router)


@app.exception_handler(PDFValidationError)
async def pdf_validation_exception_handler(
    request: Request,
    exc: PDFValidationError,
) -> JSONResponse:
    error_response = ErrorResponse(
        error="validation_error",
        message=str(exc.detail),
        request_id=exc.request_id,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(),
    )


@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse()