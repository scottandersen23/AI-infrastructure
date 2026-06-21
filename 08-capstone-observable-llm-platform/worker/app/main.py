import json
import os
import time
from datetime import UTC, datetime

try:
    import redis
except ImportError:  # pragma: no cover - allows source inspection without optional dependency
    redis = None


REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
QUEUE_NAME = os.getenv("QUEUE_NAME", "capstone:jobs")
RESULTS_NAME = os.getenv("RESULTS_NAME", "capstone:job-results")


def run_worker() -> None:
    if redis is None:
        raise RuntimeError("redis package is required to run the worker")

    client = redis.from_url(REDIS_URL, decode_responses=True)
    print(f"worker started queue={QUEUE_NAME}")
    while True:
        item = client.blpop(QUEUE_NAME, timeout=5)
        if item is None:
            continue
        _, raw_job = item
        result = process_job(json.loads(raw_job))
        client.hset(RESULTS_NAME, result["id"], json.dumps(result))


def process_job(job: dict) -> dict:
    started_at = datetime.now(UTC).isoformat()
    time.sleep(0.05)
    payload = job.get("payload", {})
    topic = payload.get("topic", "AI platform reliability")
    return {
        "id": job.get("id"),
        "status": "completed",
        "task_type": job.get("task_type", "rag_summary"),
        "started_at": started_at,
        "completed_at": datetime.now(UTC).isoformat(),
        "result": {
            "summary": (
                f"Processed '{topic}' through the capstone worker. "
                "The worker path represents long-running AI tasks decoupled from API latency."
            )
        },
    }


if __name__ == "__main__":
    run_worker()
