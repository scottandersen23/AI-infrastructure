import time
from contextlib import asynccontextmanager
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException, status
from jsonschema import ValidationError, validate
from opentelemetry.trace import Status, StatusCode

from executor.app.audit import get_connection
from executor.app.audit import record_invocation
from executor.app.config import settings
from executor.app.handlers import get_job_status, get_metrics, search_docs
from executor.app.schemas import HealthResponse, ToolInvokeRequest, ToolInvokeResponse
from executor.app.telemetry import configure_tracing, tracer

HANDLERS: dict[str, Any] = {
    "search_docs": search_docs.run,
    "get_metrics": get_metrics.run,
    "get_job_status": get_job_status.run,
}


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_tracing()
    yield


app = FastAPI(
    title="Tool Executor",
    description=(
        "Executes registered tools with argument validation. "
        "Fetches tool schemas from the registry and returns structured results."
    ),
    version="0.1.0",
    lifespan=lifespan,
)


async def fetch_tool_schema(tool_name: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"{settings.registry_url}/tools/{tool_name}")
        if response.status_code == status.HTTP_404_NOT_FOUND:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tool not registered: {tool_name}",
            )
        response.raise_for_status()
        return response.json()


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health() -> HealthResponse:
    registry_status = "ok"
    postgres_status = "ok"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.registry_url}/health")
            response.raise_for_status()
    except Exception:
        registry_status = "error"

    try:
        with get_connection() as conn:
            conn.execute("SELECT 1")
    except Exception:
        postgres_status = "error"

    return HealthResponse(
        status="ok" if registry_status == "ok" and postgres_status == "ok" else "degraded",
        service_name=settings.service_name,
        environment=settings.environment,
        dependencies={
            "registry": registry_status,
            "postgres": postgres_status,
            "rag_service": settings.rag_service_url,
            "metrics_url": settings.metrics_url,
            "jobs_api_url": settings.jobs_api_url,
        },
    )


@app.post("/invoke", response_model=ToolInvokeResponse, tags=["Tools"])
async def invoke_tool(request: ToolInvokeRequest) -> ToolInvokeResponse:
    start = time.perf_counter()
    tool_name = request.tool_name
    arguments = request.arguments

    with tracer.start_as_current_span("tool.invoke") as span:
        span.set_attribute("tool.name", tool_name)
        span.set_attribute("tool.argument_count", len(arguments))

        if tool_name not in HANDLERS:
            error_message = f"No handler implemented for tool: {tool_name}"
            latency_ms = round((time.perf_counter() - start) * 1000, 2)
            span.set_attribute("tool.success", False)
            span.set_attribute("tool.latency_ms", latency_ms)
            span.set_status(Status(StatusCode.ERROR, error_message))
            record_invocation(
                tool_name=tool_name,
                arguments=arguments,
                success=False,
                error_message=error_message,
                latency_ms=latency_ms,
            )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)

        tool_def = await fetch_tool_schema(tool_name)
        try:
            validate(instance=arguments, schema=tool_def["input_schema"])
        except ValidationError as exc:
            error_message = f"Invalid arguments for {tool_name}: {exc.message}"
            latency_ms = round((time.perf_counter() - start) * 1000, 2)
            span.set_attribute("tool.success", False)
            span.set_attribute("tool.latency_ms", latency_ms)
            span.set_status(Status(StatusCode.ERROR, error_message))
            record_invocation(
                tool_name=tool_name,
                arguments=arguments,
                success=False,
                error_message=error_message,
                latency_ms=latency_ms,
            )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=error_message,
            ) from exc

        try:
            result = await HANDLERS[tool_name](arguments)
            latency_ms = round((time.perf_counter() - start) * 1000, 2)
            span.set_attribute("tool.success", True)
            span.set_attribute("tool.latency_ms", latency_ms)
            record_invocation(
                tool_name=tool_name,
                arguments=arguments,
                success=True,
                result=result,
                latency_ms=latency_ms,
            )
            return ToolInvokeResponse(
                tool_name=tool_name,
                success=True,
                result=result,
                latency_ms=latency_ms,
            )
        except Exception as exc:
            error_message = str(exc)
            latency_ms = round((time.perf_counter() - start) * 1000, 2)
            span.set_attribute("tool.success", False)
            span.set_attribute("tool.latency_ms", latency_ms)
            span.set_status(Status(StatusCode.ERROR, error_message))
            record_invocation(
                tool_name=tool_name,
                arguments=arguments,
                success=False,
                error_message=error_message,
                latency_ms=latency_ms,
            )
            return ToolInvokeResponse(
                tool_name=tool_name,
                success=False,
                error=error_message,
                latency_ms=latency_ms,
            )
