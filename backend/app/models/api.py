from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "comply-pdf-extractor"


class ErrorResponse(BaseModel):
    error: str
    message: str
    request_id: str | None = None


class ExtractionMetadata(BaseModel):
    request_id: str
    filename: str
    page_count: int
    processing_time_ms: float


class ExtractionResponse(BaseModel):
    metadata: ExtractionMetadata
    sections: list[dict] = Field(default_factory=list)