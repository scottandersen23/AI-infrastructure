import time
import uuid
from datetime import UTC, datetime

from api.app.schemas import JobRequest, JobResponse


_JOBS: dict[uuid.UUID, JobResponse] = {}


def create_job(request: JobRequest) -> JobResponse:
    now = datetime.now(UTC)
    job = JobResponse(
        id=uuid.uuid4(),
        status="queued",
        task_type=request.task_type,
        payload=request.payload,
        created_at=now,
        updated_at=now,
    )
    _JOBS[job.id] = job
    _process_local(job.id)
    return _JOBS[job.id]


def get_job(job_id: uuid.UUID) -> JobResponse | None:
    return _JOBS.get(job_id)


def _process_local(job_id: uuid.UUID) -> None:
    job = _JOBS[job_id]
    job.status = "running"
    job.updated_at = datetime.now(UTC)
    # The Docker worker consumes Redis jobs; this local path keeps single-process
    # development deterministic without requiring Redis.
    time.sleep(0.01)
    topic = job.payload.get("topic", "AI platform reliability")
    job.status = "completed"
    job.result = {
        "summary": (
            f"Completed {job.task_type} for '{topic}'. The task reviewed platform "
            "signals across retrieval, LLM generation, async processing, and observability."
        ),
        "processed_by": "api-local-worker-fallback",
    }
    job.updated_at = datetime.now(UTC)
