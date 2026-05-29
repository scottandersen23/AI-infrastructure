from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=20_000)
    max_tokens: int = Field(default=128, ge=1, le=2_048)
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)


class GenerateResponse(BaseModel):
    model: str
    response: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    queue_wait_ms: float
    prompt_eval_ms: float
    generation_ms: float
    total_latency_ms: float
    tokens_per_second: float
    estimated_vram_mb: float


class HealthResponse(BaseModel):
    status: str
    model: str
    max_concurrent_requests: int
    simulated_vram_mb: int
