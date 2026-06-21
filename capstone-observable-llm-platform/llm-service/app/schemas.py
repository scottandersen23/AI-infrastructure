from typing import Any

from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=5_000)
    prompt: str
    sources: list[dict[str, Any]] = Field(default_factory=list)


class TokenUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class GenerateResponse(BaseModel):
    answer: str
    model_name: str
    token_usage: TokenUsage


class HealthResponse(BaseModel):
    status: str
    runtime: str
    model_name: str
