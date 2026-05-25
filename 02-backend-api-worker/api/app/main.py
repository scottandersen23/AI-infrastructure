from contextlib import asynccontextmanager
from uuid import UUID

import structlog
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from api.app.queue import check_redis, enqueue_job
from api.app.schemas import HealthResponse, JobCreateRequest, JobResponse
from api.app.validation import validate_job_payload
from shared.database import get_db, init_db
from shared.logging_config import configure_logging
from shared.models import Job, JobStatus

configure_logging("api")
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    logger.info("api_started")
    yield
    logger.info("api_stopped")


app = FastAPI(
    title="Async Job API",
    description=(
        "Production-style backend API for submitting background jobs to a Redis queue "
        "and tracking job status in PostgreSQL."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check(db: Session = Depends(get_db)) -> HealthResponse:
    postgres_status = "ok"
    redis_status = "ok"

    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        logger.error("postgres_health_check_failed", error=str(exc))
        postgres_status = "error"

    try:
        check_redis()
    except Exception as exc:
        logger.error("redis_health_check_failed", error=str(exc))
        redis_status = "error"

    overall = "ok" if postgres_status == "ok" and redis_status == "ok" else "degraded"

    if overall == "degraded":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": overall,
                "postgres": postgres_status,
                "redis": redis_status,
            },
        )

    return HealthResponse(status=overall, postgres=postgres_status, redis=redis_status)


@app.post(
    "/jobs",
    response_model=JobResponse,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["Jobs"],
)
def create_job(request: JobCreateRequest, db: Session = Depends(get_db)) -> Job:
    validated_payload = validate_job_payload(request.type, request.payload)

    job = Job(
        type=request.type,
        status=JobStatus.PENDING,
        payload=validated_payload,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    try:
        enqueue_job(job.id)
        job.status = JobStatus.QUEUED
        db.commit()
        db.refresh(job)
    except Exception as exc:
        job.status = JobStatus.FAILED
        job.error = f"Failed to enqueue job: {exc}"
        db.commit()
        db.refresh(job)
        logger.error("job_enqueue_failed", job_id=str(job.id), error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Job created but could not be queued",
        ) from exc

    logger.info("job_created", job_id=str(job.id), job_type=job.type.value)
    return job


@app.get("/jobs/{job_id}", response_model=JobResponse, tags=["Jobs"])
def get_job(job_id: UUID, db: Session = Depends(get_db)) -> Job:
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_id}' not found",
        )
    return job


@app.get("/jobs", response_model=list[JobResponse], tags=["Jobs"])
def list_jobs(limit: int = 20, db: Session = Depends(get_db)) -> list[Job]:
    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="limit must be between 1 and 100",
        )

    return (
        db.query(Job)
        .order_by(Job.created_at.desc())
        .limit(limit)
        .all()
    )
