from typing import Any


async def run(arguments: dict[str, Any]) -> dict[str, Any]:
    job_id = arguments["job_id"]

    # Stub: replace with httpx call to JOBS_API_URL when capstone API is running.
    return {
        "job_id": job_id,
        "status": "completed",
        "task_type": "rag_summary",
        "integration_status": "stub",
    }
