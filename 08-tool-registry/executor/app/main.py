import time
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException, status
from jsonschema import ValidationError, validate

from executor.app.config import settings
from executor.app.handlers import get_job_status, get_metrics, search_docs
from executor.app.schemas import HealthResponse, ToolInvokeRequest, ToolInvokeResponse

HANDLERS: dict[str, Any] = {
    "search_docs": search_docs.run,
    "get_metrics": get_metrics.run,
    "get_job_status": get_job_status.run,
}


app = FastAPI(
    title="Tool Executor",
    description=(
        "Executes registered tools with argument validation. "
        "Fetches tool schemas from the registry and returns structured results."
    ),
    version="0.1.0",
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
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.registry_url}/health")
            response.raise_for_status()
    except Exception:
        registry_status = "error"

    return HealthResponse(
        status="ok" if registry_status == "ok" else "degraded",
        service_name=settings.service_name,
        environment=settings.environment,
        dependencies={
            "registry": registry_status,
            "rag_service": settings.rag_service_url,
            "metrics_url": settings.metrics_url,
            "jobs_api_url": settings.jobs_api_url,
        },
    )


@app.post("/invoke", response_model=ToolInvokeResponse, tags=["Tools"])
async def invoke_tool(request: ToolInvokeRequest) -> ToolInvokeResponse:
    start = time.perf_counter()
    tool_name = request.tool_name

    if tool_name not in HANDLERS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No handler implemented for tool: {tool_name}",
        )

    tool_def = await fetch_tool_schema(tool_name)
    try:
        validate(instance=request.arguments, schema=tool_def["input_schema"])
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid arguments for {tool_name}: {exc.message}",
        ) from exc

    try:
        result = await HANDLERS[tool_name](request.arguments)
        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        return ToolInvokeResponse(
            tool_name=tool_name,
            success=True,
            result=result,
            latency_ms=latency_ms,
        )
    except Exception as exc:
        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        return ToolInvokeResponse(
            tool_name=tool_name,
            success=False,
            error=str(exc),
            latency_ms=latency_ms,
        )
