from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from shared.models import JobStatus, JobType


class WordCountPayload(BaseModel):
    text: str = Field(..., min_length=1, max_length=100_000)


class ReverseTextPayload(BaseModel):
    text: str = Field(..., min_length=1, max_length=100_000)


class SlowTaskPayload(BaseModel):
    seconds: int = Field(default=3, ge=1, le=30)
    message: str = Field(default="processing", max_length=500)


class JobCreateRequest(BaseModel):
    type: JobType
    payload: dict[str, Any]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "type": "word_count",
                    "payload": {"text": "hello async world"},
                },
                {
                    "type": "reverse_text",
                    "payload": {"text": "infrastructure"},
                },
                {
                    "type": "slow_task",
                    "payload": {"seconds": 5, "message": "simulated workload"},
                },
            ]
        }
    }


class JobResponse(BaseModel):
    id: UUID
    type: JobType
    status: JobStatus
    payload: dict[str, Any]
    result: dict[str, Any] | None = None
    error: str | None = None
    created_at: datetime
    updated_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}


class HealthResponse(BaseModel):
    status: str
    postgres: str
    redis: str
