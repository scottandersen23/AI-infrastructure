import json
from uuid import UUID

import redis
import structlog

from shared.config import QUEUE_NAME, REDIS_URL

logger = structlog.get_logger()
_redis_client: redis.Redis | None = None


def get_redis() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    return _redis_client


def enqueue_job(job_id: UUID) -> None:
    client = get_redis()
    client.lpush(QUEUE_NAME, str(job_id))
    logger.info("job_enqueued", job_id=str(job_id), queue=QUEUE_NAME)


def check_redis() -> str:
    client = get_redis()
    client.ping()
    return "ok"
