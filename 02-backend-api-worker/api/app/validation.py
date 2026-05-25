from typing import Any

from fastapi import HTTPException, status

from api.app.schemas import ReverseTextPayload, SlowTaskPayload, WordCountPayload
from shared.models import JobType


def validate_job_payload(job_type: JobType, payload: dict[str, Any]) -> dict[str, Any]:
    validators = {
        JobType.WORD_COUNT: WordCountPayload,
        JobType.REVERSE_TEXT: ReverseTextPayload,
        JobType.SLOW_TASK: SlowTaskPayload,
    }

    model = validators[job_type]
    try:
        validated = model.model_validate(payload)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid payload for job type '{job_type.value}': {exc}",
        ) from exc

    return validated.model_dump()
