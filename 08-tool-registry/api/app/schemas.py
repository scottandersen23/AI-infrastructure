from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    service_name: str
    environment: str
    dependencies: dict[str, str]


class ToolDefinition(BaseModel):
    name: str
    description: str
    input_schema: dict[str, Any]
    version: int = 1
    auth_scope: str = "public"
    rate_limit_rpm: int = 60
    is_active: bool = True


class ToolCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    description: str = Field(..., min_length=1)
    input_schema: dict[str, Any]
    auth_scope: str = "public"
    rate_limit_rpm: int = Field(default=60, ge=1, le=1000)


class ToolListResponse(BaseModel):
    tools: list[ToolDefinition]
    count: int
