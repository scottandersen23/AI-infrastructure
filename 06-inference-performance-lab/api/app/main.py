from fastapi import FastAPI

from api.app.config import settings
from api.app.inference import generate
from api.app.schemas import GenerateRequest, GenerateResponse, HealthResponse


app = FastAPI(
    title="Inference Performance Lab API",
    description="Mock model-serving API for measuring latency, throughput, and bottlenecks.",
    version="1.0.0",
)


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        model=settings.model_name,
        max_concurrent_requests=settings.max_concurrent_requests,
        simulated_vram_mb=settings.simulated_vram_mb,
    )


@app.post("/generate", response_model=GenerateResponse, tags=["Inference"])
async def generate_text(request: GenerateRequest) -> GenerateResponse:
    return await generate(request)
