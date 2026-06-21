import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import HTMLResponse

from api.app.clients import build_prompt, generate_answer, retrieve_context, score_quality
from api.app.config import settings
from api.app.dashboard import render_dashboard
from api.app.jobs import create_job, get_job
from api.app.metrics_store import init_metrics_store, list_events, record_event, summarize_events
from api.app.schemas import (
    AskRequest,
    AskResponse,
    HealthResponse,
    JobRequest,
    JobResponse,
    MetricEvent,
    MetricSummary,
    TokenUsage,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_metrics_store()
    yield


app = FastAPI(
    title="Observable Local LLM Platform",
    description="Capstone API gateway for RAG, local LLM serving, async jobs, and observability.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service_name=settings.service_name,
        environment=settings.environment,
        dependencies={
            "rag_service": settings.rag_service_url,
            "llm_service": settings.llm_service_url,
            "metrics_store": settings.observability_db_path,
            "redis": settings.redis_url,
        },
    )


@app.post("/ask", response_model=AskResponse, tags=["AI"])
async def ask(request: AskRequest) -> AskResponse:
    start = time.perf_counter()
    try:
        sources, retrieval_latency_ms = await retrieve_context(request.question, request.limit)
        prompt = build_prompt(request.question, sources)
        answer, model_name, token_usage, model_latency_ms = await generate_answer(
            request.question,
            prompt,
            sources,
        )
        request_latency_ms = round((time.perf_counter() - start) * 1000, 2)
        reliability = {
            "retrieval_hit": bool(sources),
            "source_count": len(sources),
            "quality_score": score_quality(sources, answer),
        }
        record_event(
            route="/ask",
            status="ok",
            request_latency_ms=request_latency_ms,
            retrieval_latency_ms=retrieval_latency_ms,
            model_latency_ms=model_latency_ms,
            token_usage=token_usage,
            retrieval_hit=reliability["retrieval_hit"],
            quality_score=reliability["quality_score"],
        )
        return AskResponse(
            answer=answer,
            sources=sources,
            prompt=prompt,
            model_name=model_name,
            request_latency_ms=request_latency_ms,
            retrieval_latency_ms=retrieval_latency_ms,
            model_latency_ms=model_latency_ms,
            token_usage=token_usage,
            reliability=reliability,
        )
    except Exception as exc:
        request_latency_ms = round((time.perf_counter() - start) * 1000, 2)
        record_event(
            route="/ask",
            status="error",
            request_latency_ms=request_latency_ms,
            retrieval_latency_ms=0,
            model_latency_ms=0,
            token_usage=TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
            retrieval_hit=False,
            quality_score=0,
            error_message=str(exc),
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Capstone ask flow failed: {exc}",
        ) from exc


@app.post("/jobs", response_model=JobResponse, tags=["Jobs"])
async def submit_job(request: JobRequest) -> JobResponse:
    return create_job(request)


@app.get("/jobs/{job_id}", response_model=JobResponse, tags=["Jobs"])
async def job_status(job_id: uuid.UUID) -> JobResponse:
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job


@app.get("/metrics/summary", response_model=MetricSummary, tags=["Observability"])
async def metrics_summary() -> MetricSummary:
    return summarize_events()


@app.get("/metrics/events", response_model=list[MetricEvent], tags=["Observability"])
async def metrics_events(limit: int = 50) -> list[MetricEvent]:
    return list_events(limit=limit)


@app.get("/dashboard", response_class=HTMLResponse, tags=["Observability"])
async def dashboard() -> str:
    return render_dashboard(summarize_events(), list_events(limit=25))
