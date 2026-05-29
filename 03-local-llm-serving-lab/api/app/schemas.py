from typing import Literal

from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=20_000)
    model: str | None = Field(default=None, description="Override the default local model.")
    system: str | None = Field(default=None, max_length=5_000)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=256, ge=1, le=8_192)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "prompt": "Explain quantization in local LLM serving in one paragraph.",
                    "model": "llama3.2:3b",
                    "temperature": 0.2,
                    "max_tokens": 180,
                }
            ]
        }
    }


class TokenUsage(BaseModel):
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None


class GenerateResponse(BaseModel):
    model: str
    runtime: str
    response: str
    latency_ms: float
    tokens_per_second: float | None = None
    usage: TokenUsage = Field(default_factory=TokenUsage)


class ModelInfo(BaseModel):
    name: str
    runtime: str
    size: int | None = None
    modified_at: str | None = None
    quantization: str | None = None


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    runtime: str
    default_model: str
    backend: str
