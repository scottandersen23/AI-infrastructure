from typing import Any

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    service_name: str
    environment: str
    dependencies: dict[str, str]


class ToolInvokeRequest(BaseModel):
    tool_name: str = Field(..., min_length=1, max_length=128)
    arguments: dict[str, Any] = Field(default_factory=dict)


class ToolInvokeResponse(BaseModel):
    tool_name: str
    success: bool
    result: dict[str, Any] | None = None
    error: str | None = None
    latency_ms: float
