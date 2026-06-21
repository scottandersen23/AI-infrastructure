from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class Source(BaseModel):
    title: str
    chunk_index: int
    similarity: float
    content: str


class TokenUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=5_000)
    limit: int = Field(default=3, ge=1, le=10)


class AskResponse(BaseModel):
    answer: str
    sources: list[Source]
    prompt: str
    model_name: str
    request_latency_ms: float
    retrieval_latency_ms: float
    model_latency_ms: float
    token_usage: TokenUsage
    reliability: dict[str, Any]


class JobRequest(BaseModel):
    task_type: str = Field(default="rag_summary", min_length=1, max_length=100)
    payload: dict[str, Any] = Field(default_factory=dict)


class JobResponse(BaseModel):
    id: UUID
    status: str
    task_type: str
    payload: dict[str, Any]
    result: dict[str, Any] | None = None
    error: str | None = None
    created_at: datetime
    updated_at: datetime


class HealthResponse(BaseModel):
    status: str
    service_name: str
    environment: str
    dependencies: dict[str, str]


class MetricEvent(BaseModel):
    id: int
    timestamp: str
    route: str
    status: str
    request_latency_ms: float
    retrieval_latency_ms: float
    model_latency_ms: float
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    retrieval_hit: bool
    quality_score: float
    error_message: str | None = None


class MetricSummary(BaseModel):
    total_requests: int
    error_count: int
    error_rate: float
    avg_request_latency_ms: float
    avg_retrieval_latency_ms: float
    avg_model_latency_ms: float
    avg_total_tokens: float
    retrieval_hit_rate: float
    avg_quality_score: float
