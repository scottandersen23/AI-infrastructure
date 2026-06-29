from typing import Any

import httpx

from executor.app.config import settings


async def run(arguments: dict[str, Any]) -> dict[str, Any]:
    job_id = arguments["job_id"]

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"{settings.jobs_api_url}/jobs/{job_id}")
        response.raise_for_status()
        payload = response.json()

    return {
        **payload,
        "integration_status": "live",
        "service_url": settings.jobs_api_url,
    }
