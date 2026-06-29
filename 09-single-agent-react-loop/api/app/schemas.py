from typing import Any
from uuid import UUID

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


class AgentRunRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=5_000)
    max_steps: int | None = Field(default=None, ge=1, le=10)
    context: dict[str, Any] = Field(default_factory=dict)


class AgentStep(BaseModel):
    step_index: int
    thought: str
    action: str | None = None
    action_input: dict[str, Any] | None = None
    observation: dict[str, Any] | None = None
    success: bool = True
    latency_ms: float | None = None
    error: str | None = None


class AgentRunResponse(BaseModel):
    run_id: UUID
    status: str
    question: str
    final_answer: str
    steps_taken: int
    max_steps: int
    steps: list[AgentStep]


class SavedAgentRun(BaseModel):
    run_id: UUID
    status: str
    question: str
    final_answer: str | None
    max_steps: int
    steps_taken: int
    error_message: str | None = None
    steps: list[AgentStep]
