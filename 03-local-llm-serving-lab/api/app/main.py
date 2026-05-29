from collections.abc import AsyncIterator

import httpx
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import StreamingResponse

from api.app.config import DEFAULT_MODEL
from api.app.runtime_clients import get_llm_client
from api.app.schemas import GenerateRequest, GenerateResponse, HealthResponse, ModelInfo

app = FastAPI(
    title="Local LLM Serving API",
    description=(
        "A small wrapper around local LLM runtimes for comparing latency, "
        "throughput, model behavior, and streaming responses."
    ),
    version="1.0.0",
)


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    client = get_llm_client()
    try:
        backend_status = await client.health()
    except Exception:
        backend_status = "unreachable"

    return HealthResponse(
        status="ok" if backend_status == "ok" else "degraded",
        runtime=client.runtime,
        default_model=DEFAULT_MODEL,
        backend=backend_status,
    )


@app.get("/models", response_model=list[ModelInfo], tags=["Models"])
async def list_models() -> list[ModelInfo]:
    client = get_llm_client()
    try:
        return await client.list_models()
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Local model runtime is unavailable: {exc}",
        ) from exc


@app.post("/generate", response_model=GenerateResponse, tags=["Generation"])
async def generate(request: GenerateRequest) -> GenerateResponse:
    client = get_llm_client()
    try:
        return await client.generate(request)
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Local model runtime is unavailable: {exc}",
        ) from exc


@app.post("/generate/stream", tags=["Generation"])
async def stream_generate(request: GenerateRequest) -> StreamingResponse:
    client = get_llm_client()

    async def stream() -> AsyncIterator[str]:
        try:
            async for chunk in client.stream_generate(request):
                yield chunk
        except httpx.HTTPError as exc:
            yield f"\n[stream_error] Local model runtime is unavailable: {exc}\n"

    return StreamingResponse(stream(), media_type="text/plain")
