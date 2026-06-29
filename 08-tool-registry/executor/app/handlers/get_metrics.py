from typing import Any

import httpx

from executor.app.config import settings


async def run(arguments: dict[str, Any]) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"{settings.metrics_url}/metrics/summary")
        response.raise_for_status()
        payload = response.json()

    return {
        **payload,
        "integration_status": "live",
        "service_url": settings.metrics_url,
    }
