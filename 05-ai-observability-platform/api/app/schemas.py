from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=5_000)
    include_debug: bool = False


class Source(BaseModel):
    title: str
    chunk_index: int
    similarity: float
    content: str


class TokenUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class AskResponse(BaseModel):
    answer: str
    sources: list[Source]
    request_latency_ms: float
    retrieval_latency_ms: float
    model_latency_ms: float
    token_usage: TokenUsage
    reliability: dict[str, Any]


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


class MetricEvent(BaseModel):
    id: int
    timestamp: datetime
    route: str
    status: str
    model_name: str
    request_latency_ms: float
    retrieval_latency_ms: float
    model_latency_ms: float
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    retrieval_hit: bool
    quality_score: float
    error_message: str | None = None


class HealthResponse(BaseModel):
    status: str
    service_name: str
    otel_exporter: str
    metrics_store: str
