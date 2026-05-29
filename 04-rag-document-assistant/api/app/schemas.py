from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class IngestRequest(BaseModel):
    path: str = Field(..., description="Markdown, text, or PDF file path to ingest.")
    title: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class IngestResponse(BaseModel):
    document_id: UUID
    title: str
    source_path: str
    chunks_created: int
    content_hash: str


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=5_000)
    limit: int = Field(default=5, ge=1, le=20)
    similarity_threshold: float | None = Field(default=None, ge=0.0, le=1.0)


class RetrievedChunk(BaseModel):
    chunk_id: UUID
    document_id: UUID
    title: str
    source_path: str
    chunk_index: int
    content: str
    similarity: float
    metadata: dict[str, Any] = Field(default_factory=dict)


class SearchResponse(BaseModel):
    query: str
    results: list[RetrievedChunk]


class AskRequest(SearchRequest):
    include_context: bool = True


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: list[RetrievedChunk]
    prompt: str | None = None


class DocumentSummary(BaseModel):
    id: UUID
    title: str
    source_path: str
    content_hash: str
    created_at: datetime
    chunk_count: int


class HealthResponse(BaseModel):
    status: str
    postgres: str
    vector_extension: str
    embedding_provider: str
