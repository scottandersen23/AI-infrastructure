import time
from typing import Any

from shared.models import JobType


def process_word_count(payload: dict[str, Any]) -> dict[str, Any]:
    text = payload["text"]
    words = text.split()
    return {
        "word_count": len(words),
        "character_count": len(text),
    }


def process_reverse_text(payload: dict[str, Any]) -> dict[str, Any]:
    text = payload["text"]
    return {
        "original": text,
        "reversed": text[::-1],
    }


def process_slow_task(payload: dict[str, Any]) -> dict[str, Any]:
    seconds = payload["seconds"]
    message = payload["message"]
    time.sleep(seconds)
    return {
        "message": message,
        "slept_seconds": seconds,
    }


TASK_HANDLERS = {
    JobType.WORD_COUNT: process_word_count,
    JobType.REVERSE_TEXT: process_reverse_text,
    JobType.SLOW_TASK: process_slow_task,
}


def run_task(job_type: JobType, payload: dict[str, Any]) -> dict[str, Any]:
    handler = TASK_HANDLERS.get(job_type)
    if handler is None:
        raise ValueError(f"Unsupported job type: {job_type}")

    return handler(payload)
