from typing import Any, Optional

from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    task_id: str
    status: str
    filename: str


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    filename: Optional[str] = None
    step: Optional[str] = None
    chunks: Optional[int] = None
    error: Optional[str] = None
    created_at: Optional[str] = None


class FileInfo(BaseModel):
    filename: str
    size: int
    created_at: float
    modified_at: float
    path: str


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    top_k: int = Field(5, ge=1, le=10)
    collection_name: Optional[str] = None


class SourceDocument(BaseModel):
    content: str
    source: str
    page: Optional[int] = None
    similarity: Optional[float] = None


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceDocument]
    processing_time_ms: int


class ReportRequest(BaseModel):
    report_type: str = Field(..., min_length=1, max_length=100)
    parameters: dict[str, Any]
    collection_name: Optional[str] = None


class ReportReference(BaseModel):
    standard_name: str
    section: Optional[str] = None
    content: Optional[str] = None


class ReportResponse(BaseModel):
    content: str
    references: list[ReportReference]
    generated_at: str
