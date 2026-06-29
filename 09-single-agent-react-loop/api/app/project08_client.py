from typing import Any

import httpx
from fastapi import HTTPException, status

from api.app.config import settings
from api.app.schemas import ToolDefinition


async def check_url(url: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{url}/health")
            response.raise_for_status()
        return "ok"
    except Exception:
        return "error"


async def list_tools() -> list[ToolDefinition]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"{settings.registry_url}/tools")
        response.raise_for_status()
        payload = response.json()

    return [ToolDefinition(**tool) for tool in payload.get("tools", [])]


async def invoke_tool(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{settings.executor_url}/invoke",
            json={"tool_name": tool_name, "arguments": arguments},
        )

    if response.status_code == status.HTTP_404_NOT_FOUND:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=response.text)

    response.raise_for_status()
    return response.json()
