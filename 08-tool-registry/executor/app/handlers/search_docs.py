from typing import Any

import httpx

from executor.app.config import settings


async def run(arguments: dict[str, Any]) -> dict[str, Any]:
    query = arguments.get("query", "")
    limit = arguments.get("limit", 5)

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(
            f"{settings.rag_service_url}/search",
            json={"query": query, "limit": limit},
        )
        response.raise_for_status()
        payload = response.json()

    return {
        "query": payload.get("query", query),
        "limit": limit,
        "sources": payload.get("results", []),
        "integration_status": "live",
        "service_url": settings.rag_service_url,
    }
