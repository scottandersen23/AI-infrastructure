from contextlib import asynccontextmanager
from time import perf_counter

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import HTMLResponse
from opentelemetry import trace

from api.app.ai_pipeline import run_observed_ai_request
from api.app.config import settings
from api.app.dashboard import render_dashboard
from api.app.metrics_store import (
    get_summary,
    init_metrics_store,
    list_recent_events,
    record_metric,
)
from api.app.schemas import AskRequest, AskResponse, HealthResponse, MetricEvent, MetricSummary
from api.app.telemetry import instrument_fastapi, tracer


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_metrics_store()
    yield


app = FastAPI(
    title="AI Observability Platform",
    description="Instrumented AI API with OpenTelemetry traces and reliability metrics.",
    version="1.0.0",
    lifespan=lifespan,
)
instrument_fastapi(app)


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service_name=settings.service_name,
        otel_exporter=settings.otel_exporter,
        metrics_store=settings.metrics_db_path,
    )


@app.post("/ask", response_model=AskResponse, tags=["AI API"])
async def ask(request: AskRequest) -> AskResponse:
    started = perf_counter()
    try:
        response = await run_observed_ai_request(request.question)
        record_metric(
            {
                "route": "/ask",
                "status": "ok",
                "model_name": settings.model_name,
                "request_latency_ms": response.request_latency_ms,
                "retrieval_latency_ms": response.retrieval_latency_ms,
                "model_latency_ms": response.model_latency_ms,
                "prompt_tokens": response.token_usage.prompt_tokens,
                "completion_tokens": response.token_usage.completion_tokens,
                "total_tokens": response.token_usage.total_tokens,
                "retrieval_hit": response.reliability["retrieval_hit"],
                "quality_score": response.reliability["quality_score"],
            }
        )
        return response
    except Exception as exc:
        latency_ms = (perf_counter() - started) * 1000
        span = trace.get_current_span()
        span.record_exception(exc)
        span.set_status(trace.Status(trace.StatusCode.ERROR, str(exc)))
        record_metric(
            {
                "route": "/ask",
                "status": "error",
                "model_name": settings.model_name,
                "request_latency_ms": latency_ms,
                "retrieval_latency_ms": 0.0,
                "model_latency_ms": 0.0,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
                "retrieval_hit": False,
                "quality_score": 0.0,
                "error_message": str(exc),
            }
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Observed AI request failed: {exc}",
        ) from exc


@app.get("/metrics/summary", response_model=MetricSummary, tags=["Metrics"])
async def metrics_summary() -> MetricSummary:
    return get_summary()


@app.get("/metrics/events", response_model=list[MetricEvent], tags=["Metrics"])
async def metrics_events(limit: int = 25) -> list[MetricEvent]:
    return list_recent_events(limit=limit)


@app.get("/dashboard", response_class=HTMLResponse, tags=["Dashboard"])
async def dashboard() -> str:
    return render_dashboard()
