import signal
import sys
from datetime import datetime, timezone
from uuid import UUID

import redis
import structlog

from shared.config import QUEUE_NAME, REDIS_URL
from shared.database import SessionLocal, init_db
from shared.logging_config import configure_logging
from shared.models import Job, JobStatus
from worker.app.tasks import run_task

configure_logging("worker")
logger = structlog.get_logger()

_shutdown = False


def handle_shutdown(signum: int, _frame) -> None:
    global _shutdown
    logger.info("shutdown_signal_received", signal=signum)
    _shutdown = True


def process_job(job_id: UUID) -> None:
    db = SessionLocal()
    try:
        job = db.get(Job, job_id)
        if job is None:
            logger.warning("job_not_found", job_id=str(job_id))
            return

        if job.status in {JobStatus.COMPLETED, JobStatus.FAILED}:
            logger.info("job_already_terminal", job_id=str(job_id), status=job.status.value)
            return

        job.status = JobStatus.RUNNING
        job.started_at = datetime.now(timezone.utc)
        db.commit()

        logger.info("job_started", job_id=str(job_id), job_type=job.type.value)

        result = run_task(job.type, job.payload)
        job.result = result
        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.now(timezone.utc)
        job.error = None
        db.commit()

        logger.info("job_completed", job_id=str(job_id), job_type=job.type.value)
    except Exception as exc:
        db.rollback()
        job = db.get(Job, job_id)
        if job is not None:
            job.status = JobStatus.FAILED
            job.error = str(exc)
            job.completed_at = datetime.now(timezone.utc)
            db.commit()
        logger.error("job_failed", job_id=str(job_id), error=str(exc))
    finally:
        db.close()


def main() -> None:
    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)

    init_db()
    client = redis.from_url(REDIS_URL, decode_responses=True)
    client.ping()

    logger.info("worker_started", queue=QUEUE_NAME, redis=REDIS_URL)

    while not _shutdown:
        item = client.brpop(QUEUE_NAME, timeout=5)
        if item is None:
            continue

        _, job_id_str = item
        try:
            job_id = UUID(job_id_str)
        except ValueError:
            logger.error("invalid_job_id", raw_value=job_id_str)
            continue

        process_job(job_id)

    logger.info("worker_stopped")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        logger.error("worker_crash", error=str(exc))
        sys.exit(1)
