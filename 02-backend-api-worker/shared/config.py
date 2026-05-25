import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://app:app@localhost:5432/jobs",
)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
QUEUE_NAME = os.getenv("QUEUE_NAME", "job_queue")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
